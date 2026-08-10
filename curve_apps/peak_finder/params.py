# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2023-2026 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from __future__ import annotations

import string
from pathlib import Path
from typing import ClassVar

import numpy as np
from geoapps_utils.base import Options
from geoh5py.data import Data, ReferencedData
from geoh5py.groups import PropertyGroup, UIJsonGroup
from geoh5py.objects import Curve

from curve_apps import assets_path


class PeakFinderParams(Options):  # pylint: disable=R0902, R0904
    """
    Parameter class for peak finder application.
    """

    name: ClassVar[str] = "peak finder"
    default_ui_json: ClassVar[Path] = assets_path() / "uijson/peak_finder.ui.json"
    title: ClassVar[str] = "Peak Finder"
    run_command: ClassVar[str] = "curve_apps.peak_finder.driver"

    conda_environment: str = "curve_apps"

    objects: Curve
    line_field: ReferencedData | None = None
    flip_sign: bool = False
    masking_data: Data | None = None
    smoothing: int = 0
    min_amplitude: int = 1
    min_value: float = -np.inf
    min_width: float = 0.0
    max_migration: float = np.inf
    min_channels: int = 1
    n_groups: int = 1
    max_separation: float = np.inf
    ga_group_name: str = "Peak Finder"
    structural_markers: bool = False
    trend_lines: bool = False
    group_a_data: PropertyGroup | None = None
    group_a_color: str | None = "#0000FF"
    group_b_data: PropertyGroup | None = None
    group_b_color: str | None = "#FFFF00"
    group_c_data: PropertyGroup | None = None
    group_c_color: str | None = "#FF0000"
    group_d_data: PropertyGroup | None = None
    group_d_color: str | None = "#00FFFF"
    group_e_data: PropertyGroup | None = None
    group_e_color: str | None = "#008000"
    group_f_data: PropertyGroup | None = None
    group_f_color: str | None = "#FFA500"
    plot_result: bool = True
    survey: Curve | None = None
    out_group: UIJsonGroup | None = None
    launch_dash: bool = False

    def get_property_groups(self):
        """
        Generate a dictionary of groups with associate properties from params.
        """
        count = 0
        property_groups = {}
        for name in string.ascii_lowercase[:6]:
            prop_group = getattr(self, f"group_{name}_data", None)
            if prop_group is not None:
                count += 1
                property_groups[prop_group.name] = {
                    "param": name,
                    "data": prop_group.uid,
                    "color": getattr(self, f"group_{name}_color", None),
                    "label": [count],
                    "properties": prop_group.properties,
                }
        return property_groups

    def get_line_field(self, survey: Curve) -> ReferencedData:
        """
        Get the line field object.
        """
        if self.line_field is None:
            unique_parts = np.unique(survey.parts.astype(int)) + 1
            line_field_obj = survey.add_data(
                {
                    "Line ID": {
                        "values": survey.parts.astype(int) + 1,
                        "value_map": {ind: f"Line {ind}" for ind in unique_parts},
                        "type": "referenced",
                    }
                }
            )
            if not isinstance(line_field_obj, ReferencedData):
                raise TypeError("Issue creating a ReferencedData'line_field'.")

            return line_field_obj

        return self.line_field
