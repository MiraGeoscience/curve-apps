# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# pylint: disable=duplicate-code

from __future__ import annotations

import logging
import sys

import numpy as np
from geoh5py.objects import Curve
from geoh5py.ui_json import InputFile, utils
from tqdm import tqdm

from curve_apps.driver import BaseCurveDriver
from curve_apps.trend_lines.params import TrendLineParameters
from curve_apps.utils import find_curves


logger = logging.getLogger(__name__)


class TrendLinesDriver(BaseCurveDriver):
    """
    Driver for the detection of trend curves across an object parts.

    :param parameters: Application parameters.
    """

    _parameter_class = TrendLineParameters

    def __init__(self, parameters: TrendLineParameters | InputFile):
        super().__init__(parameters)

    def make_curve(self):
        """Make curve object from trend lines detected in source data."""

        with utils.fetch_active_workspace(self.workspace, mode="r+") as workspace:
            logging.info("Generating trend lines ...")
            vertices, cells, labels = self.get_connections()

            if cells is None:
                logger.info("No connections found.")
                return None

            curve = Curve.create(
                workspace=workspace,
                name=self.params.output.export_as,
                vertices=vertices,
                cells=cells,
                parent=self.out_group,
            )

            if curve is not None and self.params.source.data is not None:
                curve.add_data(
                    {
                        self.params.source.data.name: {
                            "values": labels,
                            "entity_type": self.params.source.data.entity_type,
                            "association": "VERTEX",
                        }
                    }
                )

        return curve

    def get_connections(self) -> tuple:
        """
        Find connections between entity parts.

        :params entity: A Curve object with parts.
        :params data: Input referenced data.
        :params detection: Detection parameters.

        :returns : n x 3 array. Vertices of connecting lines.
        :returns : n x 2 float array. Cells of edges.
        :returns : n x 1 array. Labels of vertices.
        """
        path_list = []
        out_labels = np.zeros_like(self.labels).astype("int32")

        for value in tqdm(np.unique(self.labels), desc="Looping over data labels"):
            if value == 0:
                continue

            ind = np.where(self.labels == value)[0]

            if len(ind) < 2:
                continue

            segments = find_curves(
                self.vertices[ind, :2],
                self.parts[ind],
                self.params.detection,
            )

            if any(segments):
                path_list += ind[np.vstack(segments)].tolist()
                out_labels[ind] = value

        if any(path_list):
            path = np.vstack(path_list)

            # Truncate vertices and renumber
            verts_bool = np.zeros(self.vertices.shape[0], dtype=bool)

            uni_ind = np.unique(path.flatten())

            verts_bool[uni_ind] = True
            new_indices = np.ones_like(verts_bool, dtype="int32")
            new_indices[verts_bool] = np.arange(uni_ind.shape[0])
            path = new_indices[path]

            return (
                self.vertices[uni_ind, :],
                path,
                out_labels[uni_ind],
            )

        return self.vertices, None, out_labels

    @property
    def vertices(self) -> np.ndarray:
        """
        Get vertices from entity.
        """
        entity = self.params.source.entity
        if entity.vertices is None:
            raise ValueError("Curve must have vertices to find connections.")

        return entity.vertices

    @property
    def parts(self) -> np.ndarray:
        """
        Get parts from entity or data.
        """
        entity = self.params.source.entity
        if self.params.source.parts is not None:
            return self.params.source.parts.values

        if isinstance(entity, Curve) and entity.parts is not None:
            return entity.parts

        return np.arange(self.vertices.shape[0]).astype("int32")

    @property
    def labels(self) -> np.ndarray:
        """
        Get labels from data.
        """
        data = self.params.source.data
        if data is not None and data.values is not None:
            values = data.values
        else:
            values = np.ones_like(self.parts)

        return values


if __name__ == "__main__":
    file = sys.argv[1]
    # file = r"C:\Users\dominiquef\Desktop\parts.ui.json"
    ifile = InputFile.read_ui_json(file)

    driver = TrendLinesDriver(ifile)
    driver.run()
