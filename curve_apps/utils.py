# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import re
from collections.abc import Callable

import numpy as np
from geoapps_utils.utils.numerical import weighted_average
from geoh5py.objects import Curve, Grid2D, ObjectBase, Points, Surface
from scipy.interpolate import LinearNDInterpolator, interp1d
from scipy.spatial import Delaunay

from curve_apps.contours.params import ContourDetectionParameters
from curve_apps.trend_lines.params import TrendLineDetectionParameters


def image_to_grid_coordinate_transfer(
    image: np.ndarray, grid: list[np.ndarray]
) -> Callable:
    """
    Returns a function to interpolate from image to grid coordinates.

    :param grid: list of x and y grids.
    """
    row = np.arange(image.shape[0])
    col = np.arange(image.shape[1])
    x_interp = interp1d(col, grid[0])
    y_interp = interp1d(row, grid[1])

    def interpolator(col, row):
        return np.c_[x_interp(col), y_interp(row)]

    return interpolator


def interp_to_grid(
    entity: ObjectBase, values: np.ndarray, resolution: float, max_distance: float
) -> tuple[list[np.ndarray], np.ndarray]:
    """
    Interpolate values into a regular grid based on entity locations.

    :param entity: Geoh5py object with locations data.
    :param values: Data to be interpolated to grid.
    :param resolution: Grid resolution
    :param max_distance: Maximum distance used in weighted average.
    """

    if entity.locations is None:
        raise ValueError("Entity must have locations.")

    grid = []
    for dim in np.arange(2):
        grid += [
            np.arange(
                entity.locations[:, dim].min(),
                entity.locations[:, dim].max() + resolution,
                resolution,
            )
        ]

    x, y = np.meshgrid(grid[0], grid[1])
    z = np.zeros_like(x)
    values = weighted_average(
        entity.locations,
        np.c_[x.flatten(), y.flatten(), z.flatten()],
        [values],
        threshold=resolution / 2.0,
        n=8,
        max_distance=max_distance,
    )
    values = values[0].reshape(x.shape)

    return grid, values


def set_vertices_height(vertices: np.ndarray, entity: ObjectBase):
    """
    Uses entity z values to add height column to an Nx2 vertices array.

    :param vertices: Nx2 array of vertices.
    :param entity: geoh5py entity with vertices property.

    returns: Nx3 array of vertices.
    """
    if isinstance(entity, Points | Curve | Surface):
        if entity.vertices is None:
            raise ValueError("Entity does not have vertices.")
        z_interp = LinearNDInterpolator(
            entity.vertices[:, :2],
            entity.vertices[:, 2],
            fill_value=np.mean(entity.vertices[:, 2]),
        )
        vertices = np.c_[vertices, z_interp(vertices)]
    elif isinstance(entity, Grid2D):
        vertices = np.c_[
            vertices,
            np.ones(vertices.shape[0]) * entity.origin["z"],
        ]

    return vertices


def get_contour_list(params: ContourDetectionParameters) -> list[float]:
    """
    Compute contours requested by input parameters.

    :returns: Corresponding list of values in float format.
    """

    if (
        None not in [params.interval_min, params.interval_max, params.interval_spacing]
        and params.interval_spacing != 0
    ):
        interval_contours = np.arange(
            params.interval_min,
            params.interval_max + params.interval_spacing,  # type: ignore
            params.interval_spacing,
        ).tolist()
    else:
        interval_contours = []

    if params.fixed_contours != "" and params.fixed_contours is not None:
        if isinstance(params.fixed_contours, str):
            fixed_contours = re.split(",", params.fixed_contours.replace(" ", ""))
            fixed_contours = [float(c) for c in fixed_contours]
        elif isinstance(params.fixed_contours, float):
            fixed_contours = [params.fixed_contours]
    else:
        fixed_contours = []  # type: ignore

    contours = np.unique(np.sort(interval_contours + fixed_contours)).tolist()
    return contours


def find_curves(
    vertices: np.ndarray,
    parts: np.ndarray,
    params: TrendLineDetectionParameters | None = None,
) -> list[list[list[float]]]:
    """
    Find curves in a set of points.

    :param vertices: Vertices for points.
    :param parts: Identifier for points belong to common parts.
    :param params: Trend line detection parameters.

    :return: List of curves.
    """
    if params is None:
        params = TrendLineDetectionParameters()

    tri = Delaunay(vertices, qhull_options="QJ")
    if tri.simplices is None:  # pylint: disable=no-member
        return []

    simplices: np.ndarray = tri.simplices  # pylint: disable=no-member

    edges = np.vstack(
        (
            simplices[:, :2],
            simplices[:, 1:],
            simplices[:, ::2],
        )
    )
    edges = np.sort(edges, axis=1)
    edges = np.unique(edges, axis=0)
    distances = np.linalg.norm(vertices[edges[:, 0]] - vertices[edges[:, 1]], axis=1)
    distance_sort = np.argsort(distances)
    edges, distances = edges[distance_sort, :], distances[distance_sort]

    if params.max_distance is not None:
        edges = edges[distances <= params.max_distance, :]

    # Reject edges with same vertices id
    edge_parts = parts[edges]
    edges = edges[edge_parts[:, 0] != edge_parts[:, 1]]

    if params.azimuth is not None and params.azimuth_tol is not None:
        ind = filter_segments_orientation(
            vertices, edges, params.azimuth, params.azimuth_tol
        )
        edges = edges[ind]

    # Walk edges until no more edges can be added
    mask = np.ones(vertices.shape[0], dtype=bool)
    out_curves = []

    for ind in range(edges.shape[0]):
        if not np.any(mask[edges[ind]]):
            continue

        mask[edges[ind]] = False
        path = [edges[ind]]
        path, mask = walk_edges(
            path, edges[ind], edges, vertices, params.damping, mask=mask
        )
        path, mask = walk_edges(
            path, edges[ind][::-1], edges, vertices, params.damping, mask=mask
        )
        if len(path) < params.min_edges:
            continue

        out_curves.append(path)

    return out_curves


def walk_edges(  # pylint: disable=too-many-arguments
    path: list,
    incoming: list,
    edges: np.ndarray,
    vertices: np.ndarray,
    damping: float = 0.0,
    *,
    mask: np.ndarray | None = None,
) -> tuple[list, np.ndarray]:
    """
    Find all edges connected to a point.

    :param path: Current list of edges forming a path.
    :param incoming: Incoming edge.
    :param edges: All edges.
    :param vertices: Direction of the edges.
    :param damping: Damping factor between [0, 1] for the path roughness.
    :param mask: Mask for nodes that have already been visited.

    :return: Edges connected to point.
    """
    if mask is None:
        mask = np.ones(edges.max() + 1, dtype=bool)
        mask[np.hstack(path).flatten()] = False

    if damping < 0 or damping > 1:
        raise ValueError("Damping must be between 0 and 1.")

    neighbours = np.where(
        np.any(edges == incoming[1], axis=1) & np.any(mask[edges], axis=1)
    )[0]

    if len(neighbours) == 0:
        return path, mask

    # Outgoing candidate nodes
    candidates = edges[neighbours][edges[neighbours] != incoming[1]]

    vectors = vertices[candidates, :] - vertices[incoming[1], :]
    in_vec = np.diff(vertices[incoming, :], axis=0).flatten()
    dot = np.dot(in_vec, vectors.T)

    if not np.any(dot > 0):
        return path, mask

    # Remove backward vectors
    vectors = vectors[dot > 0, :]
    candidates = candidates[dot > 0]
    dot = dot[dot > 0]

    # Compute the angle between the incoming vector and the outgoing vectors
    vec_lengths = np.linalg.norm(vectors, axis=1)
    angle = np.arccos(dot / (np.linalg.norm(in_vec) * vec_lengths) - 1e-10)

    # Minimize the torque
    sub_ind = np.argmin(angle ** (1 - damping) * vec_lengths)
    outgoing = [incoming[1], candidates[sub_ind]]
    mask[candidates[sub_ind]] = False
    path.append(outgoing)

    # Continue walking
    path, mask = walk_edges(path, outgoing, edges, vertices, damping, mask=mask)

    return path, mask


def filter_segments_orientation(
    vertices: np.ndarray, edges: np.ndarray, azimuth: float, azimuth_tol: float
):
    """
    Filter segments orientation.

    :param vertices: Vertices for points.
    :param edges: Edges for points.
    :param azimuth: Filter angle (degree) on segments orientation, clockwise from North.
    :param azimuth_tol: Tolerance (degree) on the azimuth.

    :return: Array of boolean.
    """
    vectors = vertices[edges[:, 1], :] - vertices[edges[:, 0], :]
    test_vector = np.array([np.sin(np.deg2rad(azimuth)), np.cos(np.deg2rad(azimuth))])

    angles = np.arccos(np.dot(vectors, test_vector) / np.linalg.norm(vectors, axis=1))

    return np.logical_or(
        np.abs(angles) < np.deg2rad(azimuth_tol),
        np.abs(angles - np.pi) < np.deg2rad(azimuth_tol),
    )
