from collections.abc import Mapping
from datetime import datetime
from importlib.metadata import metadata
from types import MappingProxyType
from typing import TYPE_CHECKING, Sequence

from docutils import nodes
from sphinx import addnodes
from sphinx.domains import Domain
from sphinx.ext.intersphinx import resolve_reference_in_inventory
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from docutils.parsers.rst.states import Inliner
    from sphinx.application import Sphinx


meta = metadata("scanpy-tutorials")
project = meta["Name"]
author = meta["Author"]
copyright = f"{datetime.now():%Y}, {author}"
release = version = meta["Version"]

extensions = [
    "myst_nb",
    "sphinx.ext.intersphinx",
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

intersphinx_mapping = dict(
    scanpy=("https://scanpy.readthedocs.io/en/stable/", None),
)
# TODO: move images here from scanpy
suppress_warnings = ["image.not_readable"]

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


# Roles “implementing” {cite}`…` and {cite:p}`…`/{cite:t}`…`


def fake_cite(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: Mapping[str, object] = MappingProxyType({}),
    content: Sequence[str] = (),
) -> tuple[list[nodes.Node], list[str]]:
    msg = f"cite:{text}"
    return [
        inliner.document.reporter.info(msg),
        nodes.emphasis(rawtext, f"[{text}]"),
    ], []


class FakeDomain(Domain):
    name = "cite"
    roles = dict(p=fake_cite, t=fake_cite)


# Role linking to the canonical location in scanpy’s docs


class CanonicalTutorial(SphinxDirective):
    required_arguments = 1
    has_content = False

    def run(self) -> list[nodes.Node]:
        text = self.arguments[0]
        ref = resolve_reference_in_inventory(
            self.env,
            "scanpy",
            addnodes.pending_xref("", reftype="doc", refdomain="std", reftarget=text),
            nodes.inline("", text),
        )
        assert ref, f"Reference to scanpy:{text} not found"
        desc = nodes.inline("", "The canonical location for this document is: ")
        banner = nodes.danger(
            text,
            nodes.paragraph("", "", desc, ref),
            classes=["admonition", "caution"],
        )
        return [banner]


def setup(app: Sphinx) -> None:
    app.add_domain(FakeDomain)
    app.add_role("cite", fake_cite)
    app.add_directive("canonical-tutorial", CanonicalTutorial)
