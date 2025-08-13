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
from geoh5py import Workspace
from geoh5py.objects import Points

from curve_apps.contours.driver import ContoursDriver
from curve_apps.contours.params import ContourParameters
from curve_apps.utils import image_to_grid_coordinate_transfer


def get_contour_data(tmp_path):
    ws = Workspace(tmp_path / "test.geoh5")
    x = np.linspace(-2, 2, 99)
    y = np.linspace(-2, 2, 101)
    x_grid, y_grid = np.meshgrid(x, y)
    z_grid = (x_grid**2 + y_grid**2) - 1
    values = z_grid.flatten()
    vertices = np.c_[x_grid.flatten(), y_grid.flatten(), np.zeros_like(values)]
    pts = Points.create(ws, name="my points", vertices=vertices)
    data = pts.add_data({"my data": {"values": values}})

    params_dict = {
        "geoh5": ws,
        "objects": pts,
        "data": data,
        "fixed_contours": [0.0],
        "resolution": np.pi / 200,
        "max_distance": np.pi / 80,
        "export_as": "my curve",
    }
    params = ContourParameters.build(**params_dict)

    return params


def test_driver(tmp_path):
    params = get_contour_data(tmp_path)
    driver = ContoursDriver(params)
    driver.run()

    with params.geoh5.open():
        curve = params.geoh5.get_entity("my curve")[0]
        distances = np.linalg.norm(curve.vertices[:, :2], axis=1)
        assert np.allclose(distances, np.ones(len(distances)), atol=1e-2)


def test_image_to_grid():
    x = np.linspace(0, 10, 21)
    y = np.linspace(0, 20, 11)
    x_grid, _ = np.meshgrid(x, y)

    interp = image_to_grid_coordinate_transfer(x_grid, [x, y])
    assert np.allclose(interp(0, 0), [0, 0])
    assert np.allclose(interp(20, 10), [10, 20])
    assert np.allclose(interp(10, 5), [5, 10])
