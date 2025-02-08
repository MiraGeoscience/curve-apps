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
from geoapps_utils.utils.formatters import string_name
from geoapps_utils.utils.transformations import rotate_xyz
from geoh5py.objects import Curve, Grid2D
from geoh5py.ui_json import InputFile, utils
from skimage import measure

from curve_apps.contours.params import ContourParameters
from curve_apps.driver import BaseCurveDriver
from curve_apps.utils import (
    image_to_grid_coordinate_transfer,
    interp_to_grid,
    set_vertices_height,
)


logger = logging.getLogger(__name__)


class ContoursDriver(BaseCurveDriver):
    """
    Driver for the detection of contours within geoh5py objects.

    :param parameters: Application parameters.
    """

    _parameter_class = ContourParameters

    def __init__(self, parameters: ContourParameters | InputFile):
        super().__init__(parameters)

    def make_curve(self):
        """
        Make curve object from contours detected in source data.
        """

        with utils.fetch_active_workspace(self.workspace, mode="r+"):
            logger.info("Generating contours ...")

            entity = self.params.source.objects
            data = self.params.source.data

            if isinstance(self.params.source.objects, Grid2D):
                x_grid = entity.origin["x"] + (
                    entity.u_cell_size * np.arange(entity.shape[0])
                )
                y_grid = entity.origin["y"] + (
                    entity.v_cell_size * np.arange(entity.shape[1])
                )
                grid = [x_grid, y_grid]
                data = data.values.reshape(entity.shape[::-1], order="C")

            else:
                grid, data = interp_to_grid(
                    self.params.source.objects,
                    self.params.source.data.values,
                    self.params.detection.resolution,
                    self.params.detection.max_distance,
                )

            locations, edges, values = ContoursDriver.get_contours(
                grid, data, self.params.detection.contours
            )

            if isinstance(entity, Grid2D):
                locations = rotate_xyz(
                    locations, center=entity.origin.tolist(), theta=entity.rotation
                )

            if self.params.output.z_value:
                locations = np.c_[locations, values]
            else:
                locations = set_vertices_height(locations, self.params.source.objects)

            curve = Curve.create(
                self.workspace,
                name=string_name(self.params.output.export_as),
                vertices=locations,
                cells=edges,
                parent=self.out_group,
            )
            curve.add_data(
                {
                    self.params.source.data.name: {
                        "association": "VERTEX",
                        "values": values,
                    }
                }
            )

            return curve

    @staticmethod
    def get_contours(
        grid: list[np.ndarray], data: np.ndarray, contour_list: list[float]
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Return vertices, edges, and values for contours.

        :param grid: list of x and y grids.
        :param data: 2D array of data living in grid.
        :param contour_list: list of contour values.
        """

        interp = image_to_grid_coordinate_transfer(data, grid)
        vertices, edges, values = [], [], []
        v0 = 0
        for contour in contour_list:
            coords = measure.find_contours(data, contour)
            if not coords:
                continue

            for coord in coords:
                segment_vertices = interp(coord[:, 1], coord[:, 0])
                nv = len(segment_vertices)
                segment_edges = np.c_[np.arange(nv - 1), np.arange(1, nv)] + v0
                vertices.append(segment_vertices)
                edges.append(segment_edges)
                values.append([contour] * nv)
                v0 += nv

        if not vertices:
            raise ValueError(
                "No contours detected. Check that the requested contour "
                "values are within the bounds of the data."
            )

        return (
            np.vstack(vertices),
            np.vstack(edges).astype("uint32"),
            np.hstack(values),
        )


if __name__ == "__main__":
    file = sys.argv[1]
    ifile = InputFile.read_ui_json(file)

    driver = ContoursDriver(ifile)
    driver.run()
