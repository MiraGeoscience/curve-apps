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
from geoh5py.ui_json import InputFile
from geoh5py.workspace import Workspace

from curve_apps import assets_path
from curve_apps.contours.options import (
    ContourDetectionParameters,
    ContourParameters,
    ContourSourceParameters,
)
from curve_apps.edges.options import (
    EdgeDetectionParameters,
    EdgeParameters,
    EdgeSourceParameters,
)


def test_edge_detection_params(tmp_path):
    n_x, n_y = 10, 15
    with Workspace(tmp_path / "test.geoh5") as ws:
        grid = Grid2D.create(
            ws,
            origin=[0, 0, 0],
            u_cell_size=20.0,
            v_cell_size=30.0,
            u_count=n_x,
            v_count=n_y,
            name="my grid",
            allow_move=False,
        )
        data = grid.add_data({"my data": {"values": np.random.rand(n_x * n_y)}})

    source_params = EdgeSourceParameters(objects=grid, data=data)
    detection_params = EdgeDetectionParameters(line_length=2)
    params = EdgeParameters(geoh5=ws, source=source_params, detection=detection_params)
    assert params.title == "Edge Detection"
    assert params.run_command == "curve_apps.edges.driver"

    params.write_ui_json(tmp_path / "validation.ui.json")

    ifile = InputFile.read_ui_json(tmp_path / "validation.ui.json")
    assert ifile.data["objects"].uid == grid.uid
    assert ifile.data["data"].uid == data.uid
    assert ifile.data["line_length"] == 2
    assert ifile.data["line_gap"] == 1


def test_update_input_file(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    vertices = np.random.rand(100, 3)
    pts = Points.create(ws, vertices=vertices, name="my points")
    data = pts.add_data({"my data": {"values": np.random.rand(100)}})

    params = ContourParameters(
        geoh5=ws,
        source=ContourSourceParameters(objects=pts, data=data),
        detection=ContourDetectionParameters(fixed_contours=[0.1]),
    )

    assert params.input_file.data["fixed_contours"] == [0.1]


def test_contour_detection_params():
    params = ContourDetectionParameters(
        interval_min=0.1,
        interval_max=0.3,
        interval_spacing=0.1,
        fixed_contours=[0.0, 9.0],
    )
    assert np.allclose(params.contours, [0.0, 0.1, 0.2, 0.3, 9.0])

    params = ContourDetectionParameters(
        interval_min=0.1, interval_max=0.3, interval_spacing=0.1, fixed_contours="0, 9"
    )
    assert np.allclose(params.contours, [0.0, 0.1, 0.2, 0.3, 9.0])
    assert params.has_intervals

    params = ContourDetectionParameters(
        interval_min=0.1,
        interval_max=0.3,
        interval_spacing=0.1,
    )

    assert params.fixed_contours is None
    assert np.allclose(params.contours, [0.1, 0.2, 0.3])

    params = ContourDetectionParameters(
        fixed_contours="0, 9",
    )
    assert params.fixed_contours == [0.0, 9.0]
    assert not params.has_intervals

    with pytest.raises(ValueError, match="List of fixed contours"):
        params = ContourDetectionParameters(fixed_contours=[0.1, "lskdjf", 0.2])

    with pytest.raises(ValueError, match="Fixed contours must be a list of floats"):
        params = ContourDetectionParameters(fixed_contours=0.1)


def test_contour_params_from_uijson(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    grid = Grid2D.create(
        ws,
        origin=[0, 0, 0],
        u_cell_size=20.0,
        v_cell_size=30.0,
        u_count=10,
        v_count=10,
        name="my grid",
        allow_move=False,
    )
    data = grid.add_data({"my data": {"values": np.random.rand(100)}})

    updates = {
        "geoh5": ws,
        "objects": grid,
        "data": data,
        "interval_min": 0.1,
        "interval_max": 0.3,
        "interval_spacing": 0.1,
        "fixed_contours": "0, 9",
        "z_value": True,
        "export_as": "my contours",
    }

    ifile = InputFile.read_ui_json(
        assets_path() / "uijson/contours.ui.json", validate=False
    )
    for k, v in updates.items():
        ifile.set_data_value(k, v)

    params = ContourParameters.build(ifile)
    assert params.geoh5 == ws
    assert params.source.objects == updates["objects"]
    assert params.source.data == updates["data"]
    assert params.detection.interval_min == updates["interval_min"]
    assert params.detection.interval_max == updates["interval_max"]
    assert params.detection.interval_spacing == updates["interval_spacing"]
    assert params.detection.fixed_contours == [0.0, 9.0]
    assert params.z_value == updates["z_value"]
    assert params.export_as == updates["export_as"]
    assert params.out_group is None
