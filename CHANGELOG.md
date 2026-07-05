# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Action hardening

## [3.4.0] - 2026-05-24

### Added

- Three built-in themes: `classic` (original pydoc lavender-and-pink), `light`, and `dark`, selectable with `--theme` or `THEME` in `[tool.pydoc_fork]`. CSS variables live in `pydoc_fork/reporter/themes.py` — easy to fork.
- Tkinter GUI for driving doc generation interactively via `pydoc gui` command. New `pydoc` console script dispatches `gui` to the GUI and everything else to the normal CLI.
- `--project_name` flag and `PROJECT_NAME` config key for page headings.
- `--no_index` flag and `GENERATE_INDEX` config key to skip writing `index.html` (handy when you want your own landing page).
- `CUSTOM_TEMPLATES` config key for overriding template folder via ChoiceLoader. The Jinja loader now prefers the user's folder and falls back to bundled templates for anything missing.
- GitHub Actions workflows for build, tox, and trusted-publisher publishing with hardened action versions.
- `keepachangelog-manager` as a dev dependency.

### Changed

- Migrated build system from poetry to hatchling and uv.
- Project layout reorganized: prose docs to `rtd_docs/`, generated HTML to `docs/`, tests to `test/module_examples/`.
- Minimum Python is now 3.10. Confirmed running on Python 3.13.
- Switched argument parsing to docopt-ng.
- Reworked build/makefile and documentation regeneration script.
- Expanded README.md with usage examples, config snippets, themes table, templating section, GitHub Pages workflow, and broader prior-art comparison.

### Fixed

- Index page generation bug.
- `CUSTOM_TEMPLATES` from `[tool.pydoc_fork]` now actually honored in Jinja environment. Previously it was parsed and stored but never wired into the Jinja environment, so user templates were silently ignored.
- `PREFER_INTERNET_DOCUMENTATION` renamed to `PREFER_DOCS_PYTHON_ORG` to match settings key.
- README Python version requirement corrected to 3.10+ (was 3.8+).
- Stale README links to `docs/motivation.md`, `docs/prior_art.md`, `docs/TODO.md` repointed to `rtd_docs/`.
- `[project.urls] Changelog` in pyproject.toml corrected from non-existent `CHANGES.md` to `CHANGELOG.md`.

## [3.3.0] - 2024-02-18

### Changed

- Migrate build tooling from Pipenv and navio_tasks to a plain Makefile.
- Update GitHub Actions workflow and remove legacy config files.
- Add `__about__.py` module to centralise package metadata and version string.
- Improve internal build and CI configuration.

## [3.2.0] - 2023-05-28

### Changed

- Switched PyPI publishing to use a trusted publisher (OIDC) via GitHub Actions.

## [3.1.14] - 2021-12-09

### Fixed

- Bug fixes and improvements.

## [3.1.13] - 2021-12-02

### Fixed

- Fix multiple bugs in `commands.py`, `module_utils.py`, and reporter modules.
- Fix `settings.py` to handle missing or malformed config values.
- Expand test coverage for single-file documentation generation.

## [3.1.9] - 2021-11-28

### Fixed

- Fix `repr` handling so objects with custom `__repr__` are documented correctly.
- Regenerate all HTML documentation output.

## [3.1.8] - 2021-11-28

### Changed

- Restructure project layout and consolidate module organisation.
- Improve internal build and CI configuration.

## [3.1.4] - 2021-11-26

### Added

- First entry recoverable from commit history. Earlier 3.x and pre-3.x releases predate this changelog; consult `git log` for details.

[3.1.13]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.9...v3.1.13
[3.1.14]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.13...v3.1.14
[3.1.4]: https://github.com/matthewdeanmartin/pydoc_fork/releases/tag/v3.1.4
[3.1.8]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.4...v3.1.8
[3.1.9]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.8...v3.1.9
[3.2.0]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.14...v3.2.0
[3.3.0]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.2.0...v3.3.0
[3.4.0]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.3.0...v3.4.0
[unreleased]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.4.0...HEAD
