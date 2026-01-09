# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024-2025 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

# pylint: disable=W0613, C0302, duplicate-code


from __future__ import annotations

import uuid
from abc import ABC, abstractmethod
from typing import Any

from dash import Dash, dcc
from dash.development.base_component import Component
from geoapps_utils.base import Driver
from geoapps_utils.driver.params import BaseParams
from geoh5py.data import Data
from geoh5py.objects import ObjectBase
from geoh5py.shared.utils import fetch_active_workspace, is_uuid, stringify
from geoh5py.workspace import Workspace


# pylint: disable=too-many-positional-arguments


class BaseDashApplication(ABC):
    """
    Base class for geoapps dash applications
    """

    _param_class: type = BaseParams
    _driver_class: Driver | None = None

    def __init__(
        self,
        params: BaseParams,
        ui_json_data: dict | None = None,
    ):
        """
        Set initial ui_json_data from input file and open workspace.
        """
        self._app_initializer: dict | None = None
        self._workspace: Workspace | None = None

        if not isinstance(params, BaseParams):
            raise TypeError(
                f"Input parameters must be an instance of {BaseParams}. "
                f"Got {type(params)}"
            )

        self._params = params

        if ui_json_data is not None:
            with fetch_active_workspace(self.params.geoh5):
                for key, value in ui_json_data.items():
                    setattr(self.params, key, value)

        json_data = stringify(self.params.to_dict())

        self._ui_json_data = json_data

        if self._driver_class is not None:
            self.driver = self._driver_class(self.params)

    @property
    @abstractmethod
    def app(self) -> Dash:
        """Dash app"""

    def get_data_options(
        self,
        ui_json_data: dict,
        object_uid: str | None,
        object_name: str = "objects",
        trigger: str | None = None,
    ) -> list:
        """
        Get data dropdown options from a given object.

        :param ui_json_data: Uploaded ui.json data to read object from.
        :param object_uid: Selected object in object dropdown.
        :param object_name: Object parameter name in ui.json.
        :param trigger: Callback trigger.

        :return options: Data dropdown options.
        """
        obj = None
        with fetch_active_workspace(self.params.geoh5):
            if trigger == "ui_json_data" and object_name in ui_json_data:
                if is_uuid(ui_json_data[object_name]):
                    object_uid = ui_json_data[object_name]
                elif (
                    self.params.geoh5.get_entity(ui_json_data[object_name])[0]
                    is not None
                ):
                    object_uid = self.params.geoh5.get_entity(
                        ui_json_data[object_name]
                    )[0].uid

            if object_uid is not None and is_uuid(object_uid):
                for entity in self.params.geoh5.get_entity(uuid.UUID(object_uid)):
                    if isinstance(entity, ObjectBase):
                        obj = entity

        if obj:
            options = []
            for child in obj.children:
                if isinstance(child, Data):
                    if child.name != "Visual Parameters":
                        options.append(
                            {"label": child.name, "value": "{" + str(child.uid) + "}"}
                        )
            options = sorted(options, key=lambda d: d["label"])

            return options
        return []

    def get_params_dict(self, update_dict: dict) -> dict:
        """
        Get dict of current params.

        :param update_dict: Dict of parameters with new values to convert to a
            params dict.

        :return output_dict: Dict of current params.
        """
        if self.params is None:
            return {}

        output_dict: dict[str, Any] = {}
        # Get validations to know expected type for keys in self.params.
        validations = self.params.validations

        # Loop through self.params and update self.params with locals_dict.
        for key in self.params.to_dict():
            if key not in update_dict:
                continue
            if validations is not None:
                if bool in validations[key]["types"] and isinstance(
                    update_dict[key], list
                ):
                    # Convert from dash component checklist to bool
                    if not update_dict[key]:
                        output_dict[key] = False
                    else:
                        output_dict[key] = True
                    continue
                if (
                    float in validations[key]["types"]
                    and int not in validations[key]["types"]
                    and isinstance(update_dict[key], int)
                ):
                    # Checking for values that Dash has given as int when they
                    # should be floats.
                    output_dict[key] = float(update_dict[key])
                    continue
            if is_uuid(update_dict[key]) and self.workspace is not None:
                output_dict[key] = self.workspace.get_entity(  # pylint: disable=no-member
                    uuid.UUID(update_dict[key])
                )[0]
            else:
                output_dict[key] = update_dict[key]
        return output_dict

    @staticmethod
    def init_vals(
        layout: list[Component], ui_json_data: dict, kwargs: dict | None = None
    ):
        """
        Initialize dash components in layout from ui_json_data.

        :param layout: Dash layout.
        :param ui_json_data: Uploaded ui.json data.
        :param kwargs: Optional properties to set for components.
        """

        for comp in layout:
            BaseDashApplication._init_component(comp, ui_json_data, kwargs=kwargs)

    @staticmethod
    def _init_component(
        comp: Component, ui_json_data: dict, kwargs: dict | None = None
    ):
        """
        Initialize dash component from ui_json_data.

        :param comp: Dash component.
        :param ui_json_data: Uploaded ui.json data.
        :param kwargs: Optional properties to set for components.
        """
        if isinstance(comp, dcc.Markdown):
            return
        if hasattr(comp, "children"):
            BaseDashApplication.init_vals(comp.children, ui_json_data, kwargs)
            return

        if kwargs is not None and hasattr(comp, "id") and comp.id in kwargs:
            for prop in kwargs[comp.id]:
                setattr(comp, prop["property"], prop["value"])
            return

        if hasattr(comp, "id") and comp.id in ui_json_data:
            if isinstance(comp, dcc.Store):
                comp.data = ui_json_data[comp.id]
                return

            if isinstance(comp, dcc.Dropdown):
                comp.value = ui_json_data[comp.id]
                if comp.value is None:
                    comp.value = "None"
                if not hasattr(comp, "options"):
                    comp_option = ui_json_data[comp.id]
                    if comp_option is None:
                        comp_option = "None"
                    comp.options = [comp_option]
                return

            if isinstance(comp, dcc.Checklist):
                comp.value = []
                if ui_json_data[comp.id]:
                    comp.value = [True]

            else:
                comp.value = ui_json_data[comp.id]

    @staticmethod
    def update_visibility_from_checklist(checklist_val: list[bool]) -> dict:
        """
        Update visibility of a component from a checklist value.

        :param checklist_val: Checklist value.

        :return visibility: Component style.
        """
        if checklist_val:
            return {"display": "block"}
        return {"display": "none"}

    @property
    def params(self) -> BaseParams:
        """
        Application parameters
        """
        return self._params

    @property
    def workspace(self) -> Workspace | None:
        """
        Current workspace.
        """
        return self._workspace

    @workspace.setter
    def workspace(self, workspace):
        # Close old workspace
        if self._workspace is not None:
            self._workspace.close()
        self._workspace = workspace

    def run(
        self,
        *,
        debug: bool = False,
        port: int = 7999,
        use_reloader: bool = False,
        dev_tools_hot_reload: bool = False,
        **run_kwargs,
    ):
        """
        Run the Dash app with the provided keyword arguments.

        :param debug: If True, runs the app in debug mode. If False,
            runs the app in a native Windows, requiring the ``pywebview``
            package to be installed.
        :param port: The port number to run the app on.
        :param use_reloader: If True, enables the reloader.
        :param dev_tools_hot_reload: If True, enables hot reloading of assets.
        :param run_kwargs: Additional keyword arguments to pass to the run method.
        """
        if debug:
            self.app.run(
                debug=debug,
                port=port,
                use_reloader=use_reloader,
                dev_tools_hot_reload=dev_tools_hot_reload,
                **run_kwargs,
            )
        else:
            # pylint: disable-next=import-outside-toplevel
            from curve_apps.peak_finder.window import DashWindow

            DashWindow.show_dash_app(self.app, title=__name__)
