#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2024 Mira Geoscience Ltd.                                       '
#                                                                                '
#  All rights reserved.                                                          '
#                                                                                '
#  This file is part of curve-apps.                                              '
#                                                                                '
#  curve-apps is distributed under the terms and conditions of the MIT License   '
#  (see LICENSE file at the root of this source code package).                   '
#  '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

from curve_apps import assets_path


def test_assets_directory_exist():
    assert assets_path().is_dir()


def test_uijson_files_exists():
    assert (assets_path() / "uijson").is_dir()
    assert next(iter((assets_path() / "uijson").iterdir())).is_file()
