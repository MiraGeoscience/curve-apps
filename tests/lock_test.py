# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2023-2026 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
import tomllib
from pathlib import Path
from typing import Any

import yaml
from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def locked_pypi_names(
    entries: list[dict[str, str]], packages: dict[str, str]
) -> set[str]:
    return {
        canonicalize_name(packages[entry["pypi"]])
        for entry in entries
        if "pypi" in entry
    }


def feature_pypi_names(pixi: dict[str, Any], features: list[str]) -> set[str]:
    return {
        canonicalize_name(name)
        for feature in features
        for name in pixi.get("feature", {})
        .get(feature, {})
        .get("pypi-dependencies", {})
    }


def transitive_pypi_names(
    roots: set[str], packages: dict[str, list[dict[str, Any]]]
) -> set[str]:
    allowed = set(roots)
    pending = list(roots)
    while pending:
        for package in packages.get(pending.pop(), []):
            for requirement in package.get("requires_dist", []):
                name = canonicalize_name(Requirement(requirement).name)
                if name in packages and name not in allowed:
                    allowed.add(name)
                    pending.append(name)
    return allowed


def test_locked_pypi_names_with_git_source():
    url = "git+https://github.com/MiraGeoscience/geoh5py.git@release/ga-4.9"
    assert locked_pypi_names([{"pypi": url}], {url: "geoh5py"}) == {"geoh5py"}


def test_locked_pypi_sources():
    package_root = Path(__file__).resolve().parents[1]
    pixi = tomllib.loads((package_root / "pixi.toml").read_text())
    lock = yaml.safe_load((package_root / "pixi.lock").read_text())
    packages_by_url: dict[str, str] = {
        package["pypi"]: package["name"]
        for package in lock["packages"]
        if "pypi" in package
    }
    pypi_packages: dict[str, list[dict[str, Any]]] = {}
    for package in lock["packages"]:
        if "pypi" in package:
            pypi_packages.setdefault(canonicalize_name(package["name"]), []).append(
                package
            )

    mira_sources = feature_pypi_names(pixi, ["mira-pypi"])
    for environment, data in lock["environments"].items():
        if environment == "docs":
            continue
        features = pixi["environments"][environment]["features"]
        declared_sources = feature_pypi_names(pixi, features)
        allowed_sources = transitive_pypi_names(declared_sources, pypi_packages)

        for platform, entries in data["packages"].items():
            pypi_sources = locked_pypi_names(entries, packages_by_url)
            assert declared_sources <= pypi_sources, (
                environment,
                platform,
                declared_sources - pypi_sources,
            )
            assert pypi_sources <= allowed_sources, (
                environment,
                platform,
                pypi_sources - allowed_sources,
            )
            if "mira-pypi" in features:
                assert mira_sources <= pypi_sources, (
                    environment,
                    platform,
                    mira_sources - pypi_sources,
                )


# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#  Copyright (c) 2023-2026 Mira Geoscience Ltd.                                '
#                                                                              '
#  This file is part of curve-apps package.                                    '
#                                                                              '
#  curve-apps is distributed under the terms and conditions of the MIT License '
#  (see LICENSE file at the root of this source code package).                 '
#                                                                              '
# ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
