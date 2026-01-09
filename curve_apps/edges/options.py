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

from pathlib import Path
from typing import ClassVar

from geoapps_utils.base import Options
from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from pydantic import BaseModel, ConfigDict

from curve_apps import assets_path


class EdgeSourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param objects: A Grid2D source object.
    :param data: Data values to find edges on.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    objects: Grid2D
    data: FloatData


class EdgeDetectionParameters(BaseModel):
    """
    Edge detection parameters.

    :param line_length: Minimum accepted pixel length of detected lines. (Hough)
    :param line_gap: Maximum gap between pixels to still form a line. (Hough)
    :param sigma: Standard deviation of the Gaussian filter. (Canny)
    :param threshold: Value threshold. (Hough)
    :param window_size: Size of the window to search for lines.
    :param merge_length: Minimum length between nodes that should be merged.
    """

    line_length: int = 1
    line_gap: int = 1
    sigma: float = 10
    threshold: int = 1
    window_size: int | None = None
    merge_length: float | None = None


class EdgeParameters(Options):
    """
    Edge detection parameters for use with `edges.driver`.

    :param detection: Detection parameters expected for the edge detection.
    :param source: Parameters for the source object and data.
    :param output: Output parameters.
    """

    name: ClassVar[str] = "edges"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/edge_detection.ui.json"
    title: ClassVar[str] = "Edge Detection"
    run_command: ClassVar[str] = "curve_apps.edges.driver"

    conda_environment: str = "curve_apps"
    source: EdgeSourceParameters
    detection: EdgeDetectionParameters = EdgeDetectionParameters()
    export_as: str | None = "edges"
