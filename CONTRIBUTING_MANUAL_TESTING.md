# Manual Testing Guide for pydoc_fork UI

This document outlines the steps for human testers to verify the UI improvements, themes, and modern layouts introduced in pydoc_fork.

## Prerequisites

Ensure you have the development environment set up:

```bash
uv sync --all-extras
```

## Test Phase 1: Built-in Themes

Verify that all built-in themes render correctly.

### 1.1 Light Theme
Run:
```bash
uv run python -m pydoc_fork pydoc_fork --output test_docs/light --theme light
```
- [ ] Open `test_docs/light/pydoc_fork.html` in a browser.
- [ ] Verify background is white/light gray.
- [ ] Verify text is dark and legible.
- [ ] Verify links are blue and clear.

### 1.2 Dark Theme
Run:
```bash
uv run python -m pydoc_fork pydoc_fork --output test_docs/dark --theme dark
```
- [ ] Open `test_docs/dark/pydoc_fork.html` in a browser.
- [ ] Verify background is dark (nearly black).
- [ ] Verify text is light gray/white.
- [ ] Verify code blocks and data values have appropriate "syntax" colors.

### 1.3 Classic Theme
Run:
```bash
uv run python -m pydoc_fork pydoc_fork --output test_docs/classic --theme classic
```
- [ ] Verify it resembles the original pydoc color scheme (lavender/blue headings).

## Test Phase 2: Layout & Responsiveness

Verify the new Flexbox-based layout.

### 2.1 Multi-column Lists
- [ ] Go to a page with many modules or classes (e.g., `pydoc_fork.html`).
- [ ] Look at the "Package Contents" or "Modules" section.
- [ ] Resize the browser window.
- [ ] **Verification:** The columns should wrap or adjust based on width rather than being fixed like the old table layout.

### 2.2 Navigation Bar
- [ ] Check the top of any module page.
- [ ] **Verification:** You should see a navigation bar with "index", "source" (file link), and "Module Reference" (if applicable).
- [ ] Verify these buttons are styled as pills/buttons that change on hover.

### 2.3 Marginalia (Gutter)
- [ ] Check method/data sections.
- [ ] **Verification:** The "marginalia" (empty space on the left) should be consistently aligned.

## Test Phase 3: Configuration (pyproject.toml)

Verify that settings can be controlled via `pyproject.toml`.

1. Create a temporary `pyproject.toml` in a test directory:
```toml
[tool.pydoc_fork]
THEME = "dark"
DOCUMENT_INTERNALS = true
```
2. Run pydoc_fork from that directory.
3. **Verification:** The generated docs should use the Dark theme by default without the `--theme` flag.

## Test Phase 4: HTML5 Compliance

- [ ] Use a browser "Inspect" tool or a validator.
- [ ] **Verification:** Check that `<header>`, `<section>`, `<nav>`, and `<h1>`-`<h2>` tags are used instead of legacy `<table>` and `<font>` tags for layout.

## Reporting Issues

If you find a visual bug or a layout break:
1. Take a screenshot.
2. Note your Browser and OS.
3. Mention which theme was active.
4. File an issue on GitHub with the label `ui-regression`.
