# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
from pathlib import Path

import numpy as np
from geoh5py import Workspace
from geoh5py.data import FilenameData
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile

from curve_apps import assets_path
from curve_apps.edges.driver import EdgesDriver
from curve_apps.edges.params import EdgeParameters


def setup_example(workspace: Workspace):
    with workspace.open(mode="r+"):
        grid = Grid2D.create(
            workspace,
            origin=[128, 64, 32],
            u_cell_size=8.0,
            v_cell_size=8.0,
            u_count=128,
            v_count=64,
            dip=45.0,
            rotation=60.0,
        )

        model = np.ones((128, 64)) * 2.0
        model[16:32, 8:24] = 1.0
        model[64:72, 40:48] = 3.0
        model[120:, 40:] = np.nan
        data = grid.add_data({"values": {"values": model.flatten(order="F")}})

    return grid, data


def test_driver(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_edge_detection.geoh5")

    grid, data = setup_example(workspace)
    params = EdgeParameters.build(
        **{
            "geoh5": workspace,
            "objects": grid,
            "data": data,
            "line_length": 12,
            "line_gap": 1,
            "sigma": 1,
            "export_as": "square",
        }
    )

    driver = EdgesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]

        assert len(edges.cells) == 4  # type: ignore

    # Repeat with different window size

    params.detection.window_size = 32
    params.detection.line_gap = 1
    params.detection.line_length = 4
    params.output.export_as = "square_32"
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square_32")[0]

        assert len(edges.cells) == 22  # type: ignore


def test_merge_length(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_edge_detection.geoh5")

    grid, data = setup_example(workspace)
    params = EdgeParameters.build(
        **{
            "geoh5": workspace,
            "objects": grid,
            "data": data,
            "line_length": 12,
            "line_gap": 1,
            "sigma": 1,
            "export_as": "square",
            "merge_length": 10.0,
        }
    )

    driver = EdgesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]

        assert len(np.unique(edges.parts)) == 2  # type: ignore


def test_input_file(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_edge_detection.geoh5")

    grid, data = setup_example(workspace)
    ifile = InputFile.read_ui_json(
        assets_path() / "uijson/edge_detection.ui.json", validate=False
    )

    changes = {
        "geoh5": workspace,
        "objects": grid,
        "data": data,
        "line_length": 12,
        "line_gap": 1,
        "sigma": 1.0,
        "export_as": "square",
    }
    for key, value in changes.items():
        ifile.set_data_value(key, value)

    ifile.write_ui_json(str(tmp_path / "test_edge_detection"))
    driver = EdgesDriver(ifile)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("Edge Detection")[0]
        assert edges is not None
        assert hasattr(edges, "children")

        assert any(child for child in edges.children if isinstance(child, FilenameData))
