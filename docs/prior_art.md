## Prior Art

I'm strictly thinking of tools that turn python code into some sort of documentation, usually
based on the docstrings and object hierarchy. Out of scope are manpage documentation generators.

Docstrings are covered by a PEP, [PEP-257](https://www.python.org/dev/peps/pep-0257/)

There are many styles of "markup" for a docstring

- [Google Style](https://google.github.io/styleguide/pyguide.html)
- [RST Style](https://thomas-cokelaer.info/tutorials/sphinx/docstring_python.html), used by Sphyix
- [Epydoc](http://epydoc.sourceforge.net/)
- [Markdown](https://github.com/mkdocs/mkdocs/wiki/MkDocs-Plugins#api-documentation-building)

Standard library pydoc recognizes none of those.

## Kinds of Generators
- Live code to documentation (pydoc)
- Source code to documentation (pdoc3) (possibly some overlap with live code generators)
- Markup-to-html generators with API plugins (sphinx, mkdocs)
  - These tools assume you write documents by hand first, and as an afterthought add an API docs generator
- Markdown first (mkdocs, handsdown)
- Souce code prettifiers (pycco, pygmentize)
  - For people who need to understand the code (as opposed to just the public API)
- Abstract model generators (pytkdocs) that create JSON or the like from source
- Multilangage generator (doxygen)

## Generators
- [LazyDocs](https://pypi.org/project/lazydocs/) - API centric. Generates Markdown.
- [pytkdocs](https://github.com/mkdocstrings/pytkdocs) - Extracts docstrings to json. This is what should have been in the standard library
- [portray](https://timothycrosley.github.io/portray/) -
- [pycco](https://pycco-docs.github.io/pycco/) - Literate programming style
- [handsdown](https://github.com/vemel/handsdown) - markdown first style
- Docutils - RST generator 
- Sphinx - RST generator (needs plugin)

# Sphinx plugins
- sphinx-apidoc
- autoapi

## Linters
- [Pydocstyle](http://www.pydocstyle.org/en/6.1.1/error_codes.html) - Not sure what style this is validating.
- [Interogate](https://github.com/econchick/interrogate) - Fine grained rules on what to document,  
  e.g. skip property getters/setters
- [Pylint]() Has some rules to require docstrings
- [flake8-docstrings](https://pypi.org/project/flake8-docstrings/) Lint according to a chosen syntax
- [flake8-rst-docstrings](https://pypi.org/project/flake8-rst-docstrings/)
- 
## Formatters
- [blacken-docs](https://github.com/asottile/blacken-docs) Formats code examples in docstrings

## IDE
- Pycharm Ctrl-Q
- Pycharm Docutil RST compilation
- Pycharm Sphinx RST compilation


# to review
-
- https://github.com/twisted/pydoctor
