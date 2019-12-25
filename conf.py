from datetime import datetime
project = 'Scanpy'
author = 'Alex Wolf, Fidel Ramirez, Sergei Rybakov'
copyright = f'{datetime.now():%Y}, {author}.'

version = ''
release = version

extensions = [
    'nbsphinx',
]

templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']
pygments_style = 'sphinx'

# -- Options for HTML output ----------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_options = dict(
    navigation_depth=2, logo_only=True  # Only show the logo
)
html_context = dict(
    display_github=True,      # Integrate GitHub
    github_user='theislab',   # Username
    github_repo='scanpy-tutorials',     # Repo name
    github_version='master',  # Version
    conf_py_path='/',    # Path in the checkout to the docs root
)
html_static_path = ['_static']
html_show_sphinx = False
html_logo = '_static/img/Scanpy_Logo_BrightFG.svg'

def setup(app):
    app.add_stylesheet('css/custom.css')

# -- Strip output ----------------------------------------------

import nbclean, glob

for filename in glob.glob('**/*.ipynb', recursive=True):
    ntbk = nbclean.NotebookCleaner(filename)
    ntbk.clear('stderr')
    ntbk.save(filename)
