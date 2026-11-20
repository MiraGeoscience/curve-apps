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
    "webview",
]
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "sphinx_issues",
    "sphinxcontrib.googleanalytics",
]
intersphinx_mapping = {
    "geoh5py": ("https://mirageoscience-geoh5py.readthedocs-hosted.com/en/stable/", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
    "python": ("https://docs.python.org/3.14/", None),
}

nitpicky = True
templates_path = ["_templates"]
exclude_patterns: list[str] = []

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


def resolve_external_type(app, env, node, contnode):
    from docutils import nodes

    if node.get("refdomain") != "py":
        return None

    source_links = {
        "geoapps_utils.base.Driver": "https://github.com/MiraGeoscience/geoapps-utils/blob/release/ga-4.9/geoapps_utils/base.py#L53",
        "geoapps_utils.base.Options": "https://github.com/MiraGeoscience/geoapps-utils/blob/release/ga-4.9/geoapps_utils/base.py#L227",
        "geoapps_utils.utils.numerical.running_mean": "https://github.com/MiraGeoscience/geoapps-utils/blob/release/ga-4.9/geoapps_utils/utils/numerical.py",
        "dash.dash.Dash": "https://github.com/plotly/dash/blob/dev/dash/dash.py",
        "dash.development.base_component.Component": "https://github.com/plotly/dash/blob/dev/dash/development/base_component.py",
        "plotly.graph_objs._figure.Figure": "https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html",
    }
    target = node.get("reftarget")
    if target in source_links:
        return nodes.reference("", "", contnode, refuri=source_links[target])

    aliases = {
        "Path": "pathlib.Path",
        "Data": "geoh5py.data.data.Data",
        "FloatData": "geoh5py.data.float_data.FloatData",
        "ReferencedData": "geoh5py.data.referenced_data.ReferencedData",
        "Grid2D": "geoh5py.objects.grid2d.Grid2D",
        "Points": "geoh5py.objects.points.Points",
        "Curve": "geoh5py.objects.curve.Curve",
        "Surface": "geoh5py.objects.surface.Surface",
        "PropertyGroup": "geoh5py.groups.property_group.PropertyGroup",
        "UIJsonGroup": "geoh5py.groups.uijson.UIJsonGroup",
    }
    if target in aliases:
        node["reftarget"] = aliases[target]
    return None


def setup(app):
    app.connect("missing-reference", resolve_external_type, priority=400)