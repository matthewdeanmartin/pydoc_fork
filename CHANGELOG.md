# Changelog

All notable changes to **pydoc_fork** will be documented here.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/),
and this project follows [Semantic Versioning](https://semver.org/) — though
"semantic" is generous for a fork of pydoc.

Entries from before 3.4.0 are reconstructed from git history and may be incomplete.

## [Unreleased]

## [3.4.0] - 2026-05-24

The "themes and a GUI" release.

### Added
- Three built-in themes: `classic` (the original pydoc lavender-and-pink),
  `light`, and `dark`. Selected with `--theme` or `THEME` in
  `[tool.pydoc_fork]`. CSS variables live in
  `pydoc_fork/reporter/themes.py` — easy to fork.
- Tkinter GUI for driving doc generation interactively. Launch with
  `pydoc gui`. New `pydoc` console script dispatches `gui` to the GUI and
  everything else to the normal CLI.
- `--project_name` flag and `PROJECT_NAME` config key for the heading shown
  in generated pages.
- `--no_index` flag and `GENERATE_INDEX` config key to skip writing
  `index.html` (handy when you want your own landing page).
- `CUSTOM_TEMPLATES` config key for pointing at an override template folder.
  The Jinja loader is now a `ChoiceLoader` that prefers the user's folder and
  falls back to the bundled templates for anything missing.
- GitHub Actions workflows for build, tox, and trusted-publisher publishing
  to PyPI. Hardened action versions.
- `keepachangelog-manager` as a dev dependency so this file can be validated.

### Changed
- Migrated build system from poetry to **hatchling + uv**.
- Project layout reorganized: prose docs moved to `rtd_docs/`, generated
  HTML lives in `docs/`. Test modules moved under `test/module_examples/`.
- Minimum Python is now **3.10**.
- Confirmed running on Python 3.13.
- Switched argument parsing to **docopt-ng**.
- Reworked the build/makefile and documentation regeneration script.
- Rewrote `README.md`: expanded usage examples (themes, project name,
  `--config`, `--no_index`, `pydoc gui`), added a `[tool.pydoc_fork]`
  config snippet, a themes table, a templating section, a compact GitHub
  Pages publishing workflow, and a broader prior-art comparison
  (pydoc, pdoc/pdoc3, Sphinx, MkDocs+mkdocstrings, pdocs/portray, PyDoctor,
  Pycco, Doxygen, Read the Docs).

### Fixed
- Index page generation bug.
- `CUSTOM_TEMPLATES` (from `[tool.pydoc_fork]` in `pyproject.toml`) is now
  actually honored. Previously it was parsed and stored but never wired
  into the Jinja environment, so user templates were silently ignored.
- `[tool.pydoc_fork]` in this repo's own `pyproject.toml` used
  `PREFER_INTERNET_DOCUMENTATION`, which is not a real setting key.
  Renamed to `PREFER_DOCS_PYTHON_ORG` so it matches what
  `settings.load_config` reads.
- README documented Python 3.8+ but the package has required Python 3.10+
  since this release (per `pyproject.toml`). Corrected.
- README links to `docs/motivation.md`, `docs/prior_art.md`, and
  `docs/TODO.md` were stale — those files moved to `rtd_docs/` in this
  release. Repointed.
- `[project.urls] Changelog` in `pyproject.toml` pointed at the
  non-existent `CHANGES.md`; now points at `CHANGELOG.md`.

## [3.2.0] - 2023-05-28

### Changed
- Switched PyPI publishing to use a trusted publisher (OIDC) via GitHub
  Actions.

## [3.1.14] - 2021-12-09

### Fixed
- Miscellaneous fixes leading up to the last tagged release on the original
  cadence. (Reconstructed from commit history; specifics not recorded at
  the time.)

## [3.1.4] - 2021-11-26

### Added
- First entry recoverable from commit history. Earlier 3.x and pre-3.x
  releases predate this changelog; consult `git log` if you really need
  to know.

[Unreleased]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.4.0...HEAD
[3.4.0]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.2.0...v3.4.0
[3.2.0]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.14...v3.2.0
[3.1.14]: https://github.com/matthewdeanmartin/pydoc_fork/compare/v3.1.4...v3.1.14
[3.1.4]: https://github.com/matthewdeanmartin/pydoc_fork/releases/tag/v3.1.4
