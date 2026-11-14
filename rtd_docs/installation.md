# Installation

Requires Python 3.11 or newer. Install into the environment that can import the package you want to document:

```bash
python -m pip install pydoc_fork
```

A `pipx` installation isolates the generator from your project environment. With that isolation it can document the standard library, but it may not be able to import your project's package. For project documentation, install it alongside the project.

Verify the command is available:

```bash
pydoc_fork --version
pydoc_fork --help
```

Next, [generate your first reference](usage.md).
