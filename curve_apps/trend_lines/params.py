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

# pylint: disable=duplicate-code

from __future__ import annotations

from typing import Optional, Union

from geoapps_utils.driver.data import BaseData
from geoapps_utils.numerical import DetectionParameters
from geoh5py.data import Data, ReferencedData
from geoh5py.objects import Curve, Points
from geoh5py.ui_json import InputFile
from pydantic import BaseModel, ConfigDict

from curve_apps import assets_path

from ..params import OutputParameters

NAME = "trend_lines"
DEFAULT_UI_JSON = assets_path() / f"uijson/{NAME}.ui.json"


class SourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param entity: A Curve or Points source object.
    :param data: Data values to find edges on.
    :param parts: Optional parts to connect.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity: Union[Curve, Points]
    data: Optional[ReferencedData] = None
    parts: Optional[Data] = None


class Parameters(BaseData):
    """
    Parts connection input parameters.

    :param detection: Detection parameters expected for the parts connection.
    :param source: Parameters for the source object and data parameters.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    _name: str = NAME

    detection: DetectionParameters
    input_file: Optional[InputFile] = InputFile.read_ui_json(
        DEFAULT_UI_JSON, validate=False
    )
    output: OutputParameters
    run_command: str = f"curve_apps.{NAME}.driver"
    source: SourceParameters
    title: str = NAME.capitalize().replace("_", " ")
