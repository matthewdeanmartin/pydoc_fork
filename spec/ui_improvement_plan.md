# UI Improvement Plan for pydoc_fork

## Goals
- Complete transition to Jinja2 templating.
- Support multiple built-in themes (Light, Dark, Classic).
- Allow user customization of themes and templates.
- Modernize the look and feel using CSS Flexbox/Grid instead of tables.

## Phase 1: Bug Fixes & Infrastructure (Completed)
- [x] Fix `modules_in_current` bug in `commands.py`.
- [x] Refactor `settings.py` to support theme selection and custom template paths.
- [x] Add a `Theme` class or configuration mapping to manage CSS variables.
- [x] Conditionally use `tomllib` (Python 3.11+) or `tomli` (backport).

## Phase 2: Template Refactoring (Completed)
- [x] Create `templates/module.jinja2` to replace `docmodule` logic in `format_module.py`.
- [x] Create `templates/class.jinja2` to replace `docclass` logic in `format_class.py`.
- [x] Create `templates/function.jinja2` to replace `docroutine` logic in `format_routine.py`.
- [x] Create `templates/data.jinja2` to replace `document_data` logic in `format_data.py`.
- [x] Create `templates/multicolumn.jinja2` to replace `multicolumn` logic in `formatter_html.py`.
- [x] Move all hardcoded HTML strings from `formatter_html.py` to templates.

## Phase 3: Multi-Theme Support (Completed)
- [x] Modernize `templates/style.css` to use CSS variables for all colors and fonts.
- [x] Add built-in themes:
    - `classic`: The original pydoc look.
    - `light`: Clean, modern light theme.
    - `dark`: Eye-friendly dark theme.
- [x] Update `commands.py` to generate theme-specific `style.css`.
- [x] Add `--theme` CLI option in `__main__.py`.

## Phase 4: UI Modernization & UX (Completed)
- [x] Replace table-based layouts with Flexbox/Grid for better responsiveness.
- [x] Improve typography and spacing.
- [x] Add a simple sidebar or navigation for large modules.
- [x] Ensure HTML5 compliance across all templates.

## Phase 5: Testing & Validation (Completed)
- [x] Add visual regression tests or at least more thorough HTML structure assertions.
- [x] Verify customization by providing a custom template directory in tests.
- [x] Created CONTRIBUTING_MANUAL_TESTING.md for human validation.
