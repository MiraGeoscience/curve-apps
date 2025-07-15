# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import numpy as np
import pytest
from geoh5py.objects import Grid2D, Points
from geoh5py.workspace import Workspace

from curve_apps.trend_lines.options import TrendLineDetectionParameters
from curve_apps.utils import (
    filter_segments_orientation,
    find_curves,
    set_vertices_height,
)


def test_set_vertices_height(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    vertices = np.c_[np.random.randn(10), np.random.randn(10), np.ones(10)]
    pts = Points.create(ws, vertices=vertices, name="my points")
    new_vertices = set_vertices_height(vertices[:, :2], pts)
    assert np.allclose(vertices, new_vertices)
    grd = Grid2D.create(ws, origin=[0, 0, 1])
    new_vertices = set_vertices_height(vertices[:, :2], grd)
    assert np.allclose(vertices, new_vertices)


@pytest.fixture(name="curves_data")
def curves_data_fixture() -> list:
    # Create test data
    # Survey lines
    y_array = np.linspace(0, 50, 10)
    line_ids_array = np.arange(0, len(y_array))

    curve1 = 5 * np.sin(y_array) + 10  # curve
    curve2 = 0.7 * y_array + 20  # crossing lines
    curve3 = -0.4 * y_array + 50
    curve4 = np.ones_like(y_array) * 80  # zig-zag
    curve4[3] = 85
    curve5 = [None] * (len(y_array) - 1)  # short line
    curve5[0:1] = [60, 62]  # type: ignore
    curve5[-2:-1] = [2, 4]  # type: ignore

    curves = [curve1, curve2, curve3, curve4, curve5]

    data = []
    for channel_group, curve in enumerate(curves):
        for x_coord, y_coord, line_id in zip(
            curve, y_array, line_ids_array, strict=False
        ):
            if x_coord is not None:
                data.append([x_coord, y_coord, line_id, channel_group])
    return data


def test_find_curves(curves_data: list):
    # Random shuffle the input
    data = np.array(curves_data)
    np.random.shuffle(data)

    points_data = data[:, :2]
    line_ids = data[:, 2]
    channel_groups = data[:, 3]

    result_curves = []
    parameters = TrendLineDetectionParameters(
        min_edges=3,
        max_distance=15,
        damping=0.75,
    )
    for channel_group in np.unique(channel_groups):
        channel_inds = channel_groups == channel_group
        path = find_curves(
            points_data[channel_inds], np.array(line_ids)[channel_inds], parameters
        )

        if len(path) == 0:
            continue

        result_curves += path

    assert len(result_curves) == 4
    assert len(result_curves[3]) == 8

    # Test with different angle to get zig-zag line
    result_curves = []
    parameters = TrendLineDetectionParameters(
        min_edges=3,
        max_distance=50,
        damping=1,
    )

    for channel_group in np.unique(channel_groups):
        channel_inds = channel_groups == channel_group
        path = find_curves(
            points_data[channel_inds], np.array(line_ids)[channel_inds], parameters
        )

        result_curves += path

    assert [len(curve) for curve in result_curves] == [9, 9, 9, 9]


def test_find_curve_orientation(curves_data: list):
    # Random shuffle the input
    data = np.array(curves_data)
    points_data = data[:, :2]
    line_ids = data[:, 2]
    channel_groups = data[:, 3]

    result_curves = []

    parameters = TrendLineDetectionParameters(
        min_edges=3,
        max_distance=15,
        damping=0.75,
        azimuth=5,
        azimuth_tol=10,
    )
    for channel_group in np.unique(channel_groups):
        channel_inds = channel_groups == channel_group
        path = find_curves(
            points_data[channel_inds], np.array(line_ids)[channel_inds], parameters
        )

        if len(path) == 0:
            continue

        result_curves += path

    assert len(result_curves) == 1


def test_filter_segments_orientation():
    angles = np.arange(0, 360, 180 / 8)

    points = np.c_[
        np.sin(np.deg2rad(angles)),
        np.cos(np.deg2rad(angles)),
    ]
    points = np.r_[np.c_[0, 0], points]
    segments = np.c_[np.zeros_like(angles), np.arange(1, len(angles) + 1)].astype(int)

    ind = filter_segments_orientation(points, segments, 0, 0.1)
    np.testing.assert_allclose(angles[ind], [0, 180])

    ind = filter_segments_orientation(points, segments, 0, 30)
    np.testing.assert_allclose(angles[ind], [0, 22.5, 157.5, 180, 202.5, 337.5])

    ind = filter_segments_orientation(points, segments, -45, 30)
    np.testing.assert_allclose(angles[ind], [112.5, 135.0, 157.5, 292.5, 315.0, 337.5])

    ind = filter_segments_orientation(points, segments, -45, 360)
    assert np.all(ind)

    ind = filter_segments_orientation(points, segments, 5, 1)
    assert ~np.all(ind)  # pylint: disable=invalid-unary-operand-type
