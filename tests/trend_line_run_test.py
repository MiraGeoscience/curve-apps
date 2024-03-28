#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of curve-apps package.
#
#  All rights reserved.
#

# pylint: disable=duplicate-code

from pathlib import Path

import numpy as np
from geoh5py import Workspace
from geoh5py.data import FilenameData, ReferencedData
from geoh5py.objects import Curve, Points
from geoh5py.ui_json import InputFile

from curve_apps import assets_path
from curve_apps.trend_lines.driver import TrendLinesDriver
from curve_apps.trend_lines.params import Parameters


def setup_example(workspace: Workspace):
    with workspace.open(mode="r+"):
        y_array = np.linspace(0, 50, 10)

        curvey = 5 * np.sin(y_array) + 10
        oblique = 0.7 * y_array + 20
        straight = np.ones_like(y_array) * 30
        randos = np.random.rand(len(y_array)) * 10

        anomalies = [curvey, oblique, straight, randos]

        vertices = np.c_[
            np.hstack(anomalies),
            np.tile(y_array, len(anomalies)),
            np.zeros(len(y_array) * len(anomalies)),
        ]
        parts = np.tile(np.arange(len(y_array)), len(anomalies))
        values = np.r_[
            np.kron(np.arange(1, 4), np.ones(len(y_array))), np.zeros(len(y_array))
        ]

        curve = Curve.create(workspace=workspace, vertices=vertices, parts=parts)
        data = curve.add_data(
            {
                "values": {
                    "values": values.flatten(order="F"),
                    "value_map": {1: "A", 2: "B", 3: "C", 4: "D"},
                    "type": "referenced",
                },
            }
        )

    return curve, data


def test_driver_curve(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_trend_lines.geoh5")

    curve, data = setup_example(workspace)
    params = Parameters.build(
        {
            "geoh5": workspace,
            "entity": curve,
            "data": data,
            "export_as": "test",
        }
    )

    driver = TrendLinesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("test")[0]

        assert len(edges.cells) == 27

        values = edges.get_data("values")[0]

        assert isinstance(values, ReferencedData)
        assert values.values is not None
        assert values.value_map.map == {0: "Unknown", 1: "A", 2: "B", 3: "C", 4: "D"}


def test_driver_points(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_trend_lines.geoh5")

    curve, data = setup_example(workspace)

    with workspace.open():
        points = Points.create(workspace, vertices=curve.vertices)
        parts = points.add_data(
            {
                "parts": {
                    "values": (curve.parts + 1).astype(np.int32),
                },
            }
        )
        new_data = data.copy(parent=points)

    params = Parameters.build(
        {
            "geoh5": workspace,
            "entity": points,
            "parts": parts,
            "data": new_data,
            "export_as": "test",
        }
    )

    driver = TrendLinesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("test")[0]

        assert len(edges.cells) == 27

        values = edges.get_data("values")[0]

        assert isinstance(values, ReferencedData)
        assert values.values is not None
        assert values.value_map.map == {
            0: "Unknown",
            1: "A",
            2: "B",
            3: "C",
            4: "D",
        }


def test_driver_points_no_parts(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_trend_lines.geoh5")

    curve, data = setup_example(workspace)

    with workspace.open():
        points = Points.create(workspace, vertices=curve.vertices)
        new_data = data.copy(parent=points)

    params = Parameters.build(
        {
            "geoh5": workspace,
            "entity": points,
            "data": new_data,
            "export_as": "test",
        }
    )

    driver = TrendLinesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("test")[0]

        assert len(edges.cells) == 27

        values = edges.get_data("values")[0]

        assert isinstance(values, ReferencedData)
        assert values.values is not None
        assert values.value_map.map == {0: "Unknown", 1: "A", 2: "B", 3: "C", 4: "D"}


def test_azimuth_filter(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_trend_lines.geoh5")

    curve, data = setup_example(workspace)

    with workspace.open():
        points = Points.create(workspace, vertices=curve.vertices)
        new_data = data.copy(parent=points)

    params = Parameters.build(
        {
            "geoh5": workspace,
            "entity": points,
            "data": new_data,
            "azimuth": 35,
            "azimuth_tol": 1,
            "export_as": "test",
        }
    )

    driver = TrendLinesDriver(params)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("test")[0]

        assert len(edges.cells) == 9


def test_input_file(tmp_path: Path):
    workspace = Workspace.create(tmp_path / "test_trend_lines.geoh5")

    curve, data = setup_example(workspace)
    ifile = InputFile.read_ui_json(
        assets_path() / "uijson/trend_lines.ui.json", validate=False
    )

    changes = {
        "geoh5": workspace,
        "entity": curve,
        "data": data,
        "export_as": "square",
    }
    for key, value in changes.items():
        ifile.set_data_value(key, value)

    ifile.write_ui_json(str(tmp_path / "test_trend_lines"))
    driver = TrendLinesDriver(ifile)
    driver.run()

    with workspace.open():
        edges = workspace.get_entity("square")[0]
        assert edges is not None

        assert any(child for child in edges.children if isinstance(child, FilenameData))
