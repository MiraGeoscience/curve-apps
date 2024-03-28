#  Copyright (c) 2024 Mira Geoscience Ltd.
#
#  This file is part of edge-detection package.
#
#  All rights reserved.
#
#
#  This file is part of curve-apps.
#
#  curve-apps is distributed under the terms and conditions of the MIT License
#  (see LICENSE file at the root of this source code package).

from __future__ import annotations

from typing import Optional

from geoapps_utils.driver.data import BaseData
from geoh5py.data import FloatData
from geoh5py.objects import Grid2D
from geoh5py.ui_json import InputFile
from pydantic import BaseModel, ConfigDict

from curve_apps import assets_path

from ..params import OutputParameters

NAME = "edge_detection"
DEFAULT_UI_JSON = assets_path() / f"uijson/{NAME}.ui.json"


class SourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param objects: A Grid2D source object.
    :param data: Data values to find edges on.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    objects: Grid2D
    data: FloatData


class DetectionParameters(BaseModel):
    """
    Detection parameters expected by the ui.json file format.

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
    window_size: Optional[int] = None
    merge_length: Optional[int] = None


class Parameters(BaseData):
    """
    Edge detection input parameters.

    :param detection: Detection parameters expected for the edge detection.
    :param source: Parameters for the source object and data.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _name: str = NAME

    input_file: Optional[InputFile] = InputFile.read_ui_json(
        DEFAULT_UI_JSON, validate=False
    )
    detection: DetectionParameters
    output: OutputParameters
    run_command: str = f"curve_apps.{NAME}.driver"
    source: SourceParameters
    title: str = NAME.capitalize().replace("_", " ")
