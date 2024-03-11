from datetime import datetime
from importlib.metadata import metadata

meta = metadata("scanpy-tutorials")
project = meta["Name"]
author = meta["Author"]
copyright = f"{datetime.now():%Y}, {author}"
release = version = meta["Version"]

extensions = [
    "myst_nb",
]
myst_enable_extensions = [
    "colon_fence",
]

templates_path = ["_templates"]
source_suffix = ".rst"
master_doc = "index"
language = "en"
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "**.ipynb_checkpoints",
    "scanpy_workshop/*",
]
pygments_style = "sphinx"

# -- Options for HTML output ----------------------------------------------

html_theme = "scanpydoc"
html_theme_options = dict(
    repository_url="https://github.com/theislab/scanpy-tutorials",
    repository_branch="master",
    use_repository_button=True,
)
html_static_path = ["_static"]
html_logo = "_static/img/Scanpy_Logo_BrightFG.svg"

# -- Notebook settings ----------------------------------------------------

nb_output_stderr = "remove"
myst_heading_anchors = 3
