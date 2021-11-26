# pydoc_fork
A fork of pydoc to optimize it for generating, on a build server, html documentation for a python library you wrote

Less ambitious than the very good [pdoc3](https://pdoc3.github.io/pdoc/) and easier to use
than [Sphinx](https://www.sphinx-doc.org/en/master/)

## Installation
Requires Python 3.6+, according to `vermin`
```
pip install pydoc_fork

# or virtual environment access
pipenv install pydoc_fork

# or for global, isolated, access
pipx install pydoc_fork
```

## Usage
```
# Generate HTML for all modules and submodules from source code
> pydoc_fork my_module --output docs --document_internals

# Generate HTML for a module that is importable, e.g. sys
> pydoc_fork sys --output docs
```

## Docs
* [Motivation](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/docs/motivation.md)
* [Prior Art](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/docs/prior_art.md)
* [TODO](https://github.com/matthewdeanmartin/pydoc_fork/blob/main/docs/TODO.md)

## pydoc_fork documented in several ways:
* [pydoc_fork](https://matthewdeanmartin.github.io/pydoc_fork/docs_pydoc_fork/pydoc_fork.html)
* [Pycco](https://matthewdeanmartin.github.io/pydoc_fork/docs_pycco/index.html)
* [PyDoctor](https://matthewdeanmartin.github.io/pydoc_fork/docs_pydoctor/index.html)
* [pdoc3](https://matthewdeanmartin.github.io/pydoc_fork/docs_pdoc3/pydoc_fork/index.html)
* [mkdocstrings](https://matthewdeanmartin.github.io/pydoc_fork/docs_mkdocstrings/index.html)
* [sphinx](https://matthewdeanmartin.github.io/pydoc_fork/docs_sphinx/py-modindex.html)

## Credits
Forked from python 3.10.
https://github.com/python/cpython/blob/3.10/Lib/pydoc.py

That code is governed by this license
https://github.com/python/cpython/blob/main/LICENSE

I picked a MIT license, but I'm no lawyer, the cpython license probably governs in any conflict.
