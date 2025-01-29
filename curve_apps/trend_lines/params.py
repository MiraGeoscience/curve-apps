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

from geoapps_utils.driver.data import BaseData
from geoh5py.data import Data, ReferencedData
from geoh5py.groups import UIJsonGroup
from geoh5py.objects import Curve, Points
from pydantic import BaseModel, ConfigDict

from curve_apps import assets_path


class TrendLineSourceParameters(BaseModel):
    """
    Source parameters expected by the ui.json file format.

    :param entity: A Curve or Points source object.
    :param data: Data values to find edges on.
    :param parts: Optional parts to connect.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    entity: Curve | Points
    data: ReferencedData | None = None
    parts: Data | None = None


class TrendLineDetectionParameters(BaseModel):
    """
    Detection parameters expected by the ui.json file format.

    :param azimuth: Azimuth of the path.
    :param azimuth_tol: Tolerance for the azimuth of the path.
    :param damping: Damping factor between [0, 1] for the path roughness.
    :param min_edges: Minimum number of points in a curve.
    :param max_distance: Maximum distance between points in a curve.
    """

    azimuth: float | None = None
    azimuth_tol: float | None = None
    damping: float = 0
    min_edges: int = 1
    max_distance: float | None = None


class TrendLineOutputParameters(BaseModel):
    """
    Output parameters.

    :param export_as: Name of the output entity.
    :param out_group: Name of the output group.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    export_as: str | None = "trend_lines"
    out_group: UIJsonGroup | None = None


class TrendLineParameters(BaseData):
    """
    Trend lines parameters for use with `trend_lines.driver`.

    :param source: Source data parameters.
    :param detection: Trend line detection parameters.
    :param output: Trend line output parameters.
    """

    name: ClassVar[str] = "trend_lines"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/trend_lines.ui.json"
    title: ClassVar[str] = "Trend Lines Detection"
    run_command: ClassVar[str] = "curve_apps.trend_line_detection.driver"

    conda_environment: str = "curve_apps"
    source: TrendLineSourceParameters
    detection: TrendLineDetectionParameters
    output: TrendLineOutputParameters = TrendLineOutputParameters()
