# Usage

Run `pydoc_fork` with an importable module or package name and an output directory:

```bash
pydoc_fork my_module --output docs
```

The output contains an `index.html`, module pages, and a stylesheet. Publish the directory on a static host, or open it locally to inspect the result. The [self-documentation demo](https://matthewdeanmartin.github.io/pydoc_fork/demo/) shows real output from this project.

## Common options

```bash
# Document internal modules too
pydoc_fork my_module --output docs --document_internals

# Select a theme and add a project label
pydoc_fork my_module --output docs --theme dark --project_name "My Cool Lib"

# Link standard-library references to docs.python.org
pydoc_fork my_module --output docs --prefer_docs_python_org

# Leave the index page to another site generator
pydoc_fork my_module --output docs --no_index
```

Available themes are `classic`, `light`, and `dark`. Run `pydoc_fork --help` for the complete option list.

## Project configuration

Put reusable settings in `pyproject.toml`:

```toml
[tool.pydoc_fork]
PROJECT_NAME = "My Cool Lib"
THEME = "dark"
DOCUMENT_INTERNALS = true
PREFER_DOCS_PYTHON_ORG = true
```

Then point the CLI at the project directory:

```bash
pydoc_fork my_module --output docs --config .
```

## Templates

The generator renders pages with Jinja templates in `pydoc_fork/templates/`. To change the layout, copy the template directory, edit the copy, and set `CUSTOM_TEMPLATES` in your project configuration to the new directory.

## Publishing

See [Workflows](workflows.md) for examples of generating documentation during a build.
