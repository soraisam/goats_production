# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
# https://eikonomega.medium.com/getting-started-with-sphinx-autodoc-part-1-2cebbbca5365

project = "GOATS"
copyright = "2025, Association of Universities for Research in Astronomy"
author = "GOATS Team"

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.doctest",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.video",
    "sphinx.ext.graphviz",
]

graphviz_output_format = "svg"

templates_path = ["_templates"]

# The suffix of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"

# _static subdirectory to put videos
html_static_path = ["_static"]
html_theme = "furo"
html_logo = "images/GOATS_logo.png"
github_url = "https://github.com/gemini-hlsw/goats"
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#8244ee",
        "color-brand-content": "#8244ee",
        "color-brand-visited": "#45237f",
    },
    "dark_css_variables": {
        "color-brand-primary": "#f2aa0d",
        "color-brand-content": "#f2aa0d",
        "color-brand-visited": "#ffc23e",
    },
    # Fill out announcement to have banner appear.
    "announcement": ""
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Figure numbering
numfig = True

# Substitutions and replacements
rst_epilog = """
.. role:: raw-html(raw)
   :format: html

.. |TOMToolkit| replace:: :raw-html:`<a href="https://tom-toolkit.readthedocs.io/en/stable/">TOM Toolkit</a>`
.. |ANTARES| replace:: :raw-html:`<a href="https://antares.noirlab.edu/">ANTARES</a>`
.. |DRAGONS| replace:: :raw-html:`<a href="https://dragons.readthedocs.io/en/stable/">DRAGONS</a>`
.. |GOA| replace:: :raw-html:`<a href="https://archive.gemini.edu/">Gemini Observatory Archive</a>`
.. |Dlab| replace:: :raw-html:`<a href="https://datalab.noirlab.edu/">Astro Data Lab</a>`
.. |GPP| replace:: :raw-html:`<a href="https://noirlab.edu/public/media/archives/presentations/pdf/presentation011.pdf">Gemini Program Platform</a>`

"""
