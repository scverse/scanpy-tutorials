from datetime import datetime
from importlib.metadata import metadata

from sphinx.application import Sphinx
from myst_nb.core.render import NbElementRenderer, MimeData
from docutils import nodes

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

nb_execution_mode = "off"
nb_output_stderr = "remove"
myst_heading_anchors = 3

render_image_orig = NbElementRenderer.render_image


def render_image(self: NbElementRenderer, data: MimeData) -> list[nodes.Element]:
    """Makes images display size default to their jupyter setting.

    Workaround for: https://github.com/executablebooks/MyST-NB/issues/522
    """
    node_list = render_image_orig(self, data)
    try:
        [image] = node_list
        if not isinstance(image, nodes.image):
            raise ValueError(f"Expected nodes.image, got {type(image)}")
        for key in ("width", "height"):
            if key in image:
                continue
            if (v := data.output_metadata.get(data.mime_type, {}).get(key)) is None:
                continue
            image[key] = str(v)
    except Exception:
        return node_list
    return [image]


def setup(app: Sphinx) -> None:
    if NbElementRenderer.render_image is render_image_orig:
        NbElementRenderer.render_image = render_image
