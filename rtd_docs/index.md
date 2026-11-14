# pydoc_fork

`pydoc_fork` generates static HTML API reference pages for a Python package. Run it from a build or release workflow, then publish the output directory to a static host. It is a small fork of Python's `pydoc` focused on HTML generation.

```bash
pydoc_fork my_module --output docs
```

The generator can document modules and submodules, use classic, light, or dark styling, and link standard-library references to docs.python.org. It also supports configuration in `pyproject.toml` and custom Jinja templates.

Start with [Installation](installation.md) and [Usage](usage.md). The [generated self-documentation](https://matthewdeanmartin.github.io/pydoc_fork/demo/) shows the HTML output on this package. The [showcase gallery](https://matthewdeanmartin.github.io/pydoc_fork/#gallery) includes other documenters on the same codebase.
