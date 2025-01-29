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

import logging
import sys

import numpy as np
from geoapps_utils.utils.locations import (
    get_overlapping_limits,
    map_indices_to_coordinates,
)
from geoh5py.data import FloatData
from geoh5py.objects import Curve, Grid2D
from geoh5py.ui_json import InputFile, utils
from scipy.spatial import cKDTree
from skimage.feature import canny  # pylint: disable=no-name-in-module
from skimage.transform import (  # pylint: disable=no-name-in-module
    probabilistic_hough_line,
)

from curve_apps.driver import BaseCurveDriver
from curve_apps.edges.params import EdgeDetectionParameters, EdgeParameters


logger = logging.getLogger(__name__)


class EdgesDriver(BaseCurveDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    _parameter_class = EdgeParameters

    def __init__(self, parameters: EdgeParameters | InputFile):
        super().__init__(parameters)

    def make_curve(self):
        """
        Make curve object from edges detected in source data.

        The application relies on the Canny and Hough transforms from the
        Scikit-Image library.

        """
        with utils.fetch_active_workspace(self.workspace, mode="r+") as workspace:
            logging.info("Generated edges ...")
            canny_grid = EdgesDriver.get_canny_edges(
                self.params.source.objects,
                self.params.source.data,
                self.params.detection,
            )
            vertices, cells = EdgesDriver.get_edges(
                self.params.source.objects,
                canny_grid,
                self.params.detection,
            )

            if vertices is None or cells is None:
                return None

            self.params.source.objects.add_data(
                {"canny filter": {"values": canny_grid.flatten(order="F")}}
            )
            curve = Curve.create(
                workspace=workspace,
                name=self.params.output.export_as,
                vertices=vertices,
                cells=cells,
                parent=self.out_group,
            )

            # Compute positive angle from North
            # TODO: Move to geoapps-utils
            delta = np.c_[
                vertices[cells[:, 1], 0] - vertices[cells[:, 0], 0],
                vertices[cells[:, 1], 1] - vertices[cells[:, 0], 1],
            ]
            delta[delta[:, 0] < 0, :] *= -1
            amp = np.linalg.norm(delta, axis=1)
            orientation = np.arccos(delta[:, 1] / amp)

            # TODO: Assign values to vertices until better handling of cell data by GA
            vert_azimuth = np.zeros(curve.n_vertices) * np.nan
            vert_azimuth[cells.flatten()] = np.repeat(orientation, 2)
            curve.add_data(
                {
                    "azimuth": {"values": np.degrees(vert_azimuth)},
                }
            )

            vert_lengths = np.zeros(curve.n_vertices) * np.nan
            vert_lengths[cells.flatten()] = np.repeat(amp, 2)
            curve.add_data(
                {
                    "lengths": {"values": vert_lengths},
                }
            )

        return curve

    @staticmethod
    def get_canny_edges(
        grid: Grid2D, data: FloatData, detection: EdgeDetectionParameters
    ) -> np.ndarray:
        """
        Get edges from a grid.

        :param grid: Grid2D object.
        :param data: FloatData object.
        :param detection: Detection parameters.

        :returns: Edges from Canny transform.
        """
        if grid.shape is None or data.values is None:
            raise ValueError("Grid and data must be defined.")

        grid_data = data.values.reshape(grid.shape, order="F")

        if np.all(np.isnan(grid_data)):
            raise ValueError("No data to process.")

        # Find edges
        edges = canny(
            grid_data,
            sigma=detection.sigma,
            use_quantiles=True,
            mask=~np.isnan(grid_data),
            mode="reflect",
        )
        grid.add_data({"canny filter": {"values": edges.flatten(order="F")}})

        return edges

    @staticmethod
    def get_edges(
        grid: Grid2D,
        edges: np.ndarray,
        detection: EdgeDetectionParameters,
    ) -> tuple[np.ndarray, np.ndarray] | tuple[None, None]:
        """
        Find edges in gridded data.

        :params grid: A Grid2D object.
        :params edges: Edges representation of the grid from Canny transform.
        :params detection: Detection parameters.

        :returns : n x 3 array. Vertices of edges.
        :returns : n x 2 float array. Cells of edges.
        """
        # Find lines
        indices = EdgesDriver.get_line_indices(
            edges,
            detection.line_length,
            detection.line_gap,
            detection.threshold,
            detection.window_size,
        )

        if len(indices) == 0:
            return None, None

        pixel_coordinates = np.vstack(indices)

        if detection.merge_length is not None:
            vertices = map_indices_to_coordinates(grid, pixel_coordinates)
            tree = cKDTree(vertices)
            merge = tree.query_pairs(detection.merge_length, output_type="ndarray")
            pixel_coordinates[merge[:, 0], :] = pixel_coordinates[merge[:, 1], :]

        u_ind, r_ind = np.unique(pixel_coordinates, axis=0, return_inverse=True)
        vertices = map_indices_to_coordinates(grid, u_ind)

        cells = r_ind.reshape((-1, 2))
        return vertices, cells

    @staticmethod
    def get_line_indices(
        canny_image: np.ndarray,
        line_length: int = 1,
        line_gap: int = 1,
        threshold: int = 1,
        window_size: int | None = None,
    ) -> list:
        """
        Get indices forming lines on a canny image.

        The process is done over tiles of square size. The tiles overlap by 25%.

        :param canny_image: Edges.
        :param line_length: Minimum accepted pixel length of detected lines. (Hough)
        :param line_gap: Maximum gap between pixels to still form a line. (Hough)
        :param threshold: Value threshold. (Hough)
        :param window_size: Size of the window to search for lines.

        :returns: List of indices.
        """
        # Cycle through tiles of square size
        width = np.min(canny_image.shape)
        if window_size is not None:
            width = np.min([window_size, width])

        x_limits = get_overlapping_limits(canny_image.shape[0], width)
        y_limits = get_overlapping_limits(canny_image.shape[1], width)

        # TODO: Loop in parallel
        indices = []
        for x_lim in x_limits:
            for y_lim in y_limits:
                lines = probabilistic_hough_line(
                    canny_image[x_lim[0] : x_lim[1], y_lim[0] : y_lim[1]],
                    line_length=line_length,
                    threshold=threshold,
                    line_gap=line_gap,
                    rng=0,
                )

                if np.any(lines):
                    # Add the limits of the tile to the indices
                    lines = np.vstack(lines)[:, ::-1] + np.c_[x_lim[0], y_lim[0]]
                    indices.append(lines)

        return indices


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = EdgesDriver(ifile)
    driver.run()
