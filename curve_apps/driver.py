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
from abc import abstractmethod

from geoapps_utils.base import Driver, Options
from geoh5py.ui_json import InputFile
from geoh5py.ui_json.utils import fetch_active_workspace


logger = logging.getLogger(__name__)


class BaseCurveDriver(Driver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    _params_class: type[Options]

    def __init__(self, parameters: Options | InputFile):
        self._out_group = None
        if isinstance(parameters, InputFile):
            parameters = self._params_class.build(parameters)

        # TODO need to re-type params in base class
        super().__init__(parameters)

    @abstractmethod
    def make_curve(self):
        pass

    def run(self):
        """
        Run method of the driver.
        """
        with fetch_active_workspace(self.params.geoh5, mode="r+"):
            logging.info("Begin Process ...")
            curve = self.make_curve()
            logging.info("Process Complete.")
            self.update_monitoring_directory(curve)
