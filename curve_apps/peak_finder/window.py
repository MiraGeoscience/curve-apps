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
import threading

import webview
from dash import Dash
from waitress import serve


# Suppress verbose logging from waitress
logging.getLogger("waitress").setLevel(logging.ERROR)


class DashWindow:
    """
    A window to run and display a Dash app using pywebview.

    :param app: The Dash app to display.
    :param title: The window title.
    :param port: The port to run the Dash server on (default: 8050).
    :param host: The host to run the Dash server (default: 127.0.0.1)
    """

    def __init__(
        self, app: Dash, title: str, port: int = 8050, host: str = "127.0.0.1"
    ):
        self._app = app
        self._title = title
        self._port = port
        self._host = host
        self._url = f"http://{self._host}:{self._port}"
        self._window_open: bool = False
        self._window: webview.Window | None = None

    def _run_server(self):
        # run Dash in a thread, blocking=False
        serve(self._app.server, host=self._host, port=self._port)

    def show(self, size: tuple[int, int] = (1200, 800)):
        """
        Show the Dash app in a pywebview window.
        """
        # Start Dash server in a separate thread
        thread = threading.Thread(target=self._run_server, daemon=False)
        thread.start()

        # Open webview pointing to the Dash app
        self._window = webview.create_window(
            self._title,
            url=self._url,
            width=size[0],
            height=size[1],
            confirm_close=True,
        )

        # the icon cannot work because not in QT
        webview.start()

    @classmethod
    def show_dash_app(cls, app: Dash, title: str, size=(1200, 800)):
        """
        Show a Dash app in a PyWebView window.
        """
        window = cls(app, title)
        window.show(size)
