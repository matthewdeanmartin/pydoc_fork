# pydoc_fork

A fork of pydoc to optimize it for generating, on a build server, html documentation for a python library you wrote.

Less ambitious than the very good [pdoc3](https://pdoc3.github.io/pdoc/) and easier to use
than [Sphinx](https://www.sphinx-doc.org/en/master/). Not as pretty as either. But it works,
it's small, and the output looks like the pydoc you remember from 2003 (now with themes).

## Installation

Requires Python 3.10+

```bash
pip install pydoc_fork

# or virtual environment access
pipenv install pydoc_fork

# WARNING- installation by pipx will only allow for doc generation of the python standard library!
pipx install pydoc_fork
```

## Usage

```bash
# Generate HTML for all modules and submodules from source code
pydoc_fork my_module --output docs --document_internals

# Generate HTML for a module that is importable, e.g. sys
pydoc_fork sys --output docs

# Pick a theme and label the project
pydoc_fork my_module --output docs --theme dark --project_name "My Cool Lib"

# Link to docs.python.org for stdlib references instead of regenerating them
pydoc_fork my_module --output docs --prefer_docs_python_org

# Skip the index.html (e.g. you have your own landing page)
pydoc_fork my_module --output docs --no_index

# Use a pyproject.toml for configuration (see "Config" below)
pydoc_fork my_module --output docs --config .

# Launch the (extremely minimal) Tk GUI
pydoc gui
```

Run `pydoc_fork --help` for the full list of flags.

### Config via `pyproject.toml`

Anything you can pass on the command line you can also stash under
`[tool.pydoc_fork]` in a `pyproject.toml` and point at it with `--config <dir>`:

```toml
[tool.pydoc_fork]
PROJECT_NAME = "My Cool Lib"
THEME = "dark"
DOCUMENT_INTERNALS = true
PREFER_DOCS_PYTHON_ORG = true
GENERATE_INDEX = true
SKIP_MODULES = ["typing"]
# CUSTOM_TEMPLATES = "./my_templates"  # optional, see below
```

## Themes

Three themes ship in the box. They are CSS variables on a `:root` block, so if
you want to tweak one, fork `pydoc_fork/reporter/themes.py` — it's a single dict.

| Theme | Vibe |
|-----------|-----------------------------------------------------|
| `classic` | The original pydoc look: lavender, pink, purple. |
| `light` | A calmer modern light theme. |
| `dark` | A modern dark theme for people who code at night. |

```bash
pydoc_fork my_module --output docs --theme light
```

## Templating

Output is rendered through [Jinja2](https://jinja.palletsprojects.com/) templates
that live in `pydoc_fork/templates/`:

```
class.jinja2          function.jinja2    module.jinja2
data.jinja2           heading.jinja2     multicolumn.jinja2
disabled_text.jinja2  index.jinja2       page.jinja2
fallback.jinja2       section.jinja2
```

If you want to change the layout, copy that folder somewhere, edit, and point
`CUSTOM_TEMPLATES` at it in your `pyproject.toml`. (The plumbing for swapping
the Jinja loader is in `pydoc_fork/reporter/jinja_code.py` — keep it minimal.)

## Publishing to GitHub Pages

A compact workflow that generates docs into `./site` on every push to `main`
and publishes them. Drop it at `.github/workflows/docs.yml`:

```yaml
name: docs
on:
  push:
    branches: [main]
permissions:
  contents: read
  pages: write
  id-token: write
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deploy.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install . pydoc_fork
      - run: pydoc_fork my_module --output site --theme light --project_name "My Cool Lib"
      - uses: actions/upload-pages-artifact@v3
        with: { path: site }
      - id: deploy
        uses: actions/deploy-pages@v4
```

One-time setup: in your repo, **Settings → Pages → Build and deployment →
Source: GitHub Actions**. After the first successful run the URL will appear at
the top of the Pages settings panel and in the workflow summary.

## Docs

- [Motivation](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/rtd_docs/motivation.md)
- [Prior Art](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/rtd_docs/prior_art.md)
- [TODO](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/rtd_docs/TODO.md)

## pydoc_fork documented in several ways

Because the best way to evaluate a doc generator is to see it run on the same
codebase as its peers:

- [pydoc_fork](https://matthewdeanmartin.github.io/pydoc_fork/docs_pydoc_fork/pydoc_fork.html)
- [Pycco](https://matthewdeanmartin.github.io/pydoc_fork/docs_pycco/index.html)
- [PyDoctor](https://matthewdeanmartin.github.io/pydoc_fork/docs_pydoctor/index.html)
- [pdoc3](https://matthewdeanmartin.github.io/pydoc_fork/docs_pdoc3/pydoc_fork/index.html)
- [mkdocstrings](https://matthewdeanmartin.github.io/pydoc_fork/docs_mkdocstrings/index.html)
- [sphinx](https://matthewdeanmartin.github.io/pydoc_fork/docs_sphinx/py-modindex.html)

## Prior art and alternatives

pydoc_fork exists because none of these were quite the right shape for
"generate API HTML on a build server and forget about it." They are all,
however, excellent at what they do — try them first.

- **[pydoc](https://docs.python.org/3/library/pydoc.html)** — the stdlib
  original. The direct ancestor of this fork. Great for `pydoc -p 0` at a
  REPL; awkward for "render all of my package to a folder of HTML in CI."
- **[pdoc3](https://pdoc3.github.io/pdoc/)** / **[pdoc](https://pdoc.dev/)** —
  the closest peers. Nicer output, more features, more configuration surface.
  If you want the output to look modern out of the box, start here.
- **[Sphinx](https://www.sphinx-doc.org/)** — the heavyweight. Unmatched for
  narrative documentation, cross-references, and multi-format output. Has a
  learning curve, a `conf.py`, an `index.rst`, themes, extensions, and
  opinions. Worth it for large projects.
- **[MkDocs](https://www.mkdocs.org/)** + **[mkdocstrings](https://mkdocstrings.github.io/)** —
  Markdown-first sites with API docs injected via `::: module.name`. Lovely
  output (especially with the Material theme), but it is a site generator
  first and an API extractor second.
- **[pdocs](https://timothycrosley.github.io/pdocs/)** /
  **[portray](https://timothycrosley.github.io/portray/)** — Timothy Crosley's
  duo. Portray is "MkDocs + pdocs + zero config" — very nice if your project
  fits the mold.
- **[PyDoctor](https://github.com/twisted/pydoctor)** — the original API doc
  tool for Twisted. Strict about docstring formatting, produces dense
  reference output.
- **[Pycco](https://pycco-docs.github.io/pycco/)** — literate-style
  side-by-side source/docs. Different goal, but worth knowing about.
- **[Doxygen](https://www.doxygen.nl/)** — yes, it does Python. No, you
  probably don't want it for Python.
- **[Read the Docs](https://about.readthedocs.com/)** — not a generator but a
  hosting platform; pairs with Sphinx or MkDocs. The "obvious" alternative to
  the GitHub Pages workflow above.

If you are starting a new project and want something modern with a thriving
community, pick pdoc or mkdocstrings. If you want output that screams "this is
the API and nothing else, rendered the way pydoc has always rendered it" and
you want to call it from a one-line shell script in CI, this fork is for you.

## Credits

Forked from [pydoc in python 3.10](https://github.com/python/cpython/blob/3.10/Lib/pydoc.py).

That code is governed by the cpython [license](https://github.com/python/cpython/blob/main/LICENSE)

I picked a MIT license, but I'm no lawyer, the cpython license probably governs in any conflict.
