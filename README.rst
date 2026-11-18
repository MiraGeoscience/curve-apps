|coverage| |precommit_ci| |docs| |style| |version| |status| |pyversions|


.. |docs| image:: https://readthedocs.com/projects/mirageoscience-curve-apps/badge/?version=latest
    :alt: Documentation Status
    :target: https://mirageoscience-curve-apps.readthedocs-hosted.com/en/latest/?badge=latest

.. |coverage| image:: https://codecov.io/gh/MiraGeoscience/curve-apps/branch/develop/graph/badge.svg
    :alt: Code coverage
    :target: https://codecov.io/gh/MiraGeoscience/curve-apps

.. |style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :alt: Coding style
    :target: https://github.com/pf/black

.. |version| image:: https://img.shields.io/pypi/v/curve-apps.svg
    :alt: version on PyPI
    :target: https://pypi.python.org/pypi/curve-apps/

.. |status| image:: https://img.shields.io/pypi/status/curve-apps.svg
    :alt: version status on PyPI
    :target: https://pypi.python.org/pypi/curve-apps/

.. |pyversions| image:: https://img.shields.io/pypi/pyversions/curve-apps.svg
    :alt: Python versions
    :target: https://pypi.python.org/pypi/curve-apps/

.. |precommit_ci| image:: https://results.pre-commit.ci/badge/github/MiraGeoscience/curve-apps/develop.svg
    :alt: pre-commit.ci status
    :target: https://results.pre-commit.ci/latest/github/MiraGeoscience/curve-apps/develop

.. TODO: configure Code Climate and add top |maintainability| link new |coverage|
    .. |maintainability| image:: https://api.codeclimate.com/v1/badges/_token_/maintainability
    :target: https://codeclimate.com/github/MiraGeoscience/curve-apps/maintainability
    :alt: Maintainability



curve-apps
==========

Auto-detection of trends and edges in geoscientific data.

.. contents:: Table of Contents
   :local:
   :depth: 3

Documentation
^^^^^^^^^^^^^
`Online documentation <https://mirageoscience-curve-apps.readthedocs-hosted.com/en/latest/>`_


Installation
^^^^^^^^^^^^
**curve-apps** requires Python 3.12 or newer.

Install Pixi
------------

Install `Pixi <https://pixi.sh/>`_ version 0.84.2 or newer.

From a checkout of **curve-apps**, install the locked runtime and the local package with::

    pixi run --frozen --environment runtime install

The package is installed in editable mode, so source changes are immediately reflected at runtime.
Keep the source directory in place.

Activate the runtime environment with::

    pixi shell --frozen --environment runtime

Setup for development
^^^^^^^^^^^^^^^^^^^^^
To configure the development environment and tools, please see `README-dev.rst`_.

.. _README-dev.rst: README-dev.rst

License
^^^^^^^
MIT License

Copyright (c) 2023-2025 Mira Geoscience

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


Third Party Software
^^^^^^^^^^^^^^^^^^^^
The curve-apps Software may provide links to third party libraries or code (collectively "Third Party Software")
to implement various functions. Third Party Software does not comprise part of the Software.
The use of Third Party Software is governed by the terms of such software license(s).
Third Party Software notices and/or additional terms and conditions are located in the
`THIRD_PARTY_SOFTWARE.rst`_ file.

.. _THIRD_PARTY_SOFTWARE.rst: ./docs/source/THIRD_PARTY_SOFTWARE.rst

Copyright
^^^^^^^^^
Copyright (c) 2023-2026 Mira Geoscience Ltd.
