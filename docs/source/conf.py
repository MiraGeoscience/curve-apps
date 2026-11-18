# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
from datetime import datetime
from importlib.metadata import version as get_version

from packaging.version import Version

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "curve-apps"
author = "Mira Geoscience Ltd."
project_copyright = "%Y, Mira Geoscience Ltd"

package_name = "curve-apps"

full_version = Version(get_version(package_name))
release = full_version.public
if full_version.is_postrelease:
    release = release.rsplit(".post", 1)[0]
version = full_version.base_version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
autodoc_mock_imports = [
    "numpy",
    "geoh5py",
    "scipy",
    "skimage",
    "geoapps_utils",
    "pydantic",
    "tqdm",
    "webview",
    "dash",
    "dash_daq",
    "dash_bootstrap_components",
]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_issues",
    "sphinxcontrib.googleanalytics",
]
intersphinx_mapping = {
    "numpy": ("https://numpy.org/doc/stable/", None),
    "python": ("https://docs.python.org/3.14/", None),
}

nitpicky = True
templates_path = ["_templates"]
exclude_patterns: list[str] = []
todo_include_todos = True

googleanalytics_id = os.environ.get("GOOGLE_ANALYTICS_ID", "")
googleanalytics_enabled = bool(googleanalytics_id)

issues_github_path = f"mirageoscience/{package_name}"

# -- Options for auto-doc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
autodoc_typehints = "signature"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = "alabaster"
html_logo = "_static/logo.png"
html_static_path = ["_static/custom.css"]
html_theme_options = {
    "logo_name": "peak-finder",
    "fixed_sidebar": True,
    "description": f"version {release}",
    "show_relbars": True,
}

# Enable numref
numfig = True

def get_copyright_notice():
    return f"Copyright {datetime.now().strftime(project_copyright)}"

rst_epilog = f"""
.. |copyright_notice| replace:: {get_copyright_notice()}.
"""