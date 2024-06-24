from collections.abc import Mapping
from datetime import datetime
from importlib.metadata import metadata
from types import MappingProxyType
from typing import TYPE_CHECKING, Sequence, cast

from docutils import nodes
from sphinx import addnodes
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.ext.intersphinx import resolve_reference_in_inventory

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
intersphinx_disabled_reftypes = []
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
    node = inliner.document.reporter.info(f"cite:{text}")
    return [node], []


class FakeDomain(Domain):
    name = "cite"
    roles = dict(p=fake_cite, t=fake_cite)


# Role linking to the canonical location in scanpy’s docs


def canonical_tutorial(
    name: str,
    rawtext: str,
    text: str,
    lineno: int,
    inliner: Inliner,
    options: Mapping[str, object] = MappingProxyType({}),
    content: Sequence[str] = (),
) -> tuple[list[nodes.Node], list[str]]:
    env = cast(BuildEnvironment, inliner.document.settings.env)
    # TODO: do a big banner thing here
    node = resolve_reference_in_inventory(
        env,
        "scanpy",
        addnodes.pending_xref(text, reftype="doc", refdomain="std", reftarget=text),
        nodes.inline(rawtext, text),
    )
    assert node
    return [node], []


def setup(app: Sphinx) -> None:
    app.add_domain(FakeDomain)
    app.add_role("cite", fake_cite)
    app.add_role("canonical-tutorial", canonical_tutorial)
