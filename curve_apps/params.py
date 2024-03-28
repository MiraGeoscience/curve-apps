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

from pydantic import BaseModel


class OutputParameters(BaseModel):
    """
    Output parameters expected by the ui.json file format.

    :param export_as: Name of the output entity.
    :param out_group: Name of the output group.
    """

    export_as: Optional[str] = None
    out_group: Optional[str] = None
