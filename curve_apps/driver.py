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

import logging
import tempfile
from abc import abstractmethod

from geoapps_utils.driver.data import BaseData
from geoapps_utils.driver.driver import BaseDriver
from geoh5py.groups import ContainerGroup
from geoh5py.objects import ObjectBase
from geoh5py.ui_json import InputFile

logger = logging.getLogger(__name__)


class BaseCurveDriver(BaseDriver):
    """
    Driver for the edge detection application.

    :param parameters: Application parameters.
    """

    _parameter_class: type[BaseData]
    _default_name: str

    def __init__(self, parameters: BaseData | InputFile):
        if isinstance(parameters, InputFile):
            parameters = self._parameter_class.build(parameters)

        # TODO need to re-type params in base class
        super().__init__(parameters)

    def run(self):
        """
        Run method of the driver.
        """
        with self.workspace.open(mode="r+") as workspace:
            parent = None
            if self.params.output.out_group is not None:
                parent = ContainerGroup.create(
                    workspace=workspace,
                    name=self.params.output.out_group,
                )

            name = self.params.output.export_as
            if name is None:
                name = self._default_name

            logger.info("Begin process.")
            output = self.create_output(name, parent=parent)
            logger.info("Process completed.")

            if output is not None:
                self.update_monitoring_directory(
                    parent if parent is not None else output
                )

            logger.info("Curve object '%s' saved to '%s'.", name, str(workspace.h5file))

    @abstractmethod
    def create_output(self, name: str, parent: ContainerGroup | None = None):
        """
        Create output.
        """

    @property
    def params(self) -> BaseData:
        """Application parameters."""
        return self._params

    @params.setter
    def params(self, val: BaseData):
        if not isinstance(val, BaseData):
            raise TypeError("Parameters must be of type Parameters.")
        self._params = val

    def add_ui_json(self, entity: ObjectBase | ContainerGroup):
        """
        Add ui.json file to entity.

        :param entity: Object to add ui.json file to.
        """
        param_dict = self.params.flatten()
        self.params.input_file.update_ui_values(param_dict)

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = self.params.input_file.write_ui_json(
                path=temp_dir, name=self.params.name + ".ui.json"
            )
            entity.add_file(str(file_path))
