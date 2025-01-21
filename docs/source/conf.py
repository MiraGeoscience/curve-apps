# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

from importlib.metadata import version
from datetime import datetime

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "curve-apps"

# The full version, including alpha/beta/rc tags.
release = version("curve-apps")
# The short X.Y.Z version.
version = ".".join(release.split(".")[:3])


project_copyright = "%Y, Mira Geoscience Ltd"

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
]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.todo",
]
nitpicky = True

templates_path = ["_templates"]
exclude_patterns: list[str] = []
todo_include_todos = True

# -- Options for auto-doc ----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc

autodoc_typehints = "signature"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = [""]
html_theme_options = {
    'description': f"version {release}",
}

# Enable numref
numfig = True

def get_copyright_notice():
    return f"Copyright {datetime.now().strftime(project_copyright)}"

rst_epilog = f"""
.. |copyright_notice| replace:: {get_copyright_notice()}.
"""