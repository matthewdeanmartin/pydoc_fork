UV ?= uv
MAKEFLAGS += --no-print-directory
export PYTHONUTF8 := 1

PACKAGE := pydoc_fork
PYTHON_TARGETS := pydoc_fork test
PYLINT_MAIN_TARGETS := pydoc_fork
PYLINT_TEST_TARGETS := test
MARKDOWN_TARGETS := README.md CHANGELOG.md AGENTS.md
YAML_TARGETS := .github mkdocs.yml
GHA_WORKFLOWS := .github/workflows
ABOUT_FILE := pydoc_fork/__about__.py

.PHONY: \
	sync \
	pre-commit-install \
	format format-python format-yaml format-markdown \
	format-check format-check-python format-check-yaml format-check-markdown \
	lint lint-check ruff-fix ruff-check pylint pylint-tests pylint-spelling \
	spell \
	docs-check docs-check-docstrings docs-check-links docs-check-pydoctest griffe \
	build-docs \
	make-docs make-docs-pdoc make-docs-mkdocs \
	sample-docs sample-docs-dark dogfood \
	dead-code vulture deadcode \
	explore refurb crosshair deptry import-linter \
	security bandit audit \
	smoke test test-ci tox \
	typecheck typecheck-mypy \
	metadata metadata-check version-check dev-status \
	gha-validate gha-pin gha-upgrade publish-gha \
	prerelease publish-check publish \
	check check-ci \
	clean clean-pyc clean-test \
	help

help:
	@echo "Targets:"
	@echo "  sync                    Install / refresh dependencies"
	@echo "  pre-commit-install      Install pre-commit hooks into .git/hooks"
	@echo ""
	@echo "  format                  Auto-format all code and markup"
	@echo "  format-check            Check formatting without changes"
	@echo "  lint                    Ruff fix + pylint (main + tests)"
	@echo "  lint-check              Ruff check + pylint (read-only)"
	@echo "  spell                   Spell-check code, docs, and README"
	@echo ""
	@echo "  test                    Run pytest suite with coverage"
	@echo "  test-ci                 Run pytest -n auto (parallel, for CI)"
	@echo "  tox                     Run tests across py39-py313 via tox-uv"
	@echo "  smoke                   CLI smoke checks (--help, --version)"
	@echo ""
	@echo "  typecheck               Run mypy"
	@echo "  security                Run bandit + uv audit + pip-audit"
	@echo ""
	@echo "  metadata                Regenerate __about__.py from pyproject.toml"
	@echo "  metadata-check          Verify __about__.py is in sync"
	@echo "  version-check           Verify version consistency (jiggle_version)"
	@echo "  dev-status              Verify Development Status classifier"
	@echo ""
	@echo "  docs-check              All doc checks (docstrings + links + pydoctest)"
	@echo "  docs-check-docstrings   interrogate docstring coverage"
	@echo "  docs-check-pydoctest    pydoctest docstring example tests"
	@echo "  docs-check-links        linkcheckMarkdown"
	@echo "  griffe                  griffe API surface check (advisory)"
	@echo "  build-docs              Build mkdocs documentation"
	@echo ""
	@echo "  make-docs               Generate all doc formats (pdoc + mkdocs)"
	@echo "  make-docs-pdoc          Generate pdoc HTML docs"
	@echo "  make-docs-mkdocs        Build mkdocs docs"
	@echo "  sample-docs             Self-document pydoc_fork (light theme)"
	@echo "  sample-docs-dark        Self-document pydoc_fork (dark theme)"
	@echo "  dogfood                 Run both sample-docs variants"
	@echo ""
	@echo "  dead-code               vulture + deadcode (advisory, non-blocking)"
	@echo ""
	@echo "  explore                 All four exploratory tools in sequence"
	@echo "  refurb                  Modern Python idiom suggestions (advisory)"
	@echo "  crosshair               Symbolic execution / contract checking (advisory)"
	@echo "  deptry                  Unused / missing / misplaced deps (advisory)"
	@echo "  import-linter           Enforce import architecture contracts (advisory)"
	@echo ""
	@echo "  gha-validate            YAML parse + artifact handoff check + zizmor"
	@echo "  gha-pin                 Pin GHA action refs to commit SHAs"
	@echo "  gha-upgrade             Pin + validate (gha-pin then gha-validate)"
	@echo "  publish-gha             Dispatch the GitHub Actions publish workflow"
	@echo ""
	@echo "  check                   Full local quality gate"
	@echo "  check-ci                CI quality gate (no formatting mutations)"
	@echo "  prerelease              All checks before publishing"
	@echo "  publish-check           Build wheel and list dist/ contents"
	@echo "  publish                 Publish via uv (OIDC or UV_PUBLISH_TOKEN)"

# ── Setup ─────────────────────────────────────────────────────────────────────

sync:
	@$(UV) sync

pre-commit-install:
	@$(UV) run pre-commit install

# ── Formatting ────────────────────────────────────────────────────────────────

format: format-python format-yaml format-markdown

format-python:
	@$(UV) run isort $(PYTHON_TARGETS)
	@$(UV) run black $(PYTHON_TARGETS)
	@$(UV) run ruff check --fix --quiet $(PYTHON_TARGETS)
	@$(UV) run black $(PYTHON_TARGETS)

format-yaml:
	@$(UV) run yamlfix $(YAML_TARGETS)

format-markdown:
	@$(UV) run mdformat $(MARKDOWN_TARGETS)

format-check: format-check-python format-check-yaml format-check-markdown

format-check-python:
	@$(UV) run isort --check-only $(PYTHON_TARGETS)
	@$(UV) run black --check $(PYTHON_TARGETS)
	@$(UV) run ruff check --quiet $(PYTHON_TARGETS)

format-check-yaml:
	@$(UV) run yamlfix --check $(YAML_TARGETS)

format-check-markdown:
	@$(UV) run mdformat --check $(MARKDOWN_TARGETS)

# ── Linting ───────────────────────────────────────────────────────────────────

lint: ruff-fix pylint pylint-tests

lint-check: ruff-check pylint pylint-tests

ruff-fix:
	@$(UV) run ruff check --fix --quiet $(PYTHON_TARGETS)

ruff-check:
	@$(UV) run ruff check --quiet $(PYTHON_TARGETS)

pylint:
	@$(UV) run pylint --score=n --reports=n --rcfile=.pylintrc $(PYLINT_MAIN_TARGETS)

pylint-tests:
	@$(UV) run pylint --score=n --reports=n --rcfile=.pylintrc_tests $(PYLINT_TEST_TARGETS) || true

pylint-spelling:
	@$(UV) run pylint --score=n --reports=n --rcfile=.pylintrc_spell $(PYLINT_MAIN_TARGETS)

# ── Spell check ───────────────────────────────────────────────────────────────

spell: pylint-spelling
	@$(UV) run codespell --ignore-words=private_dictionary.txt \
		--skip="test/support" \
		$(PACKAGE) test README.md CHANGELOG.md AGENTS.md

# ── Documentation checks ─────────────────────────────────────────────────────

docs-check: docs-check-docstrings docs-check-pydoctest docs-check-links

docs-check-docstrings:
	@$(UV) run interrogate $(PACKAGE) --verbose --fail-under 70

docs-check-pydoctest:
	@$(UV) run pydoctest --config .pydoctest.json \
		| grep -v "__init__" | grep -v "__main__" | grep -v "Unable to parse" || true

docs-check-links:
	@$(UV) run linkcheckMarkdown README.md || true

griffe:
	@echo "=== griffe API surface check (advisory) ==="
	@$(UV) run griffe check $(PACKAGE) || true

# ── Documentation generation ─────────────────────────────────────────────────
# pydoc_fork can generate docs multiple ways; preserve all of them.

make-docs-pdoc:
	@$(UV) run pdoc $(PACKAGE) --html -o docs --force

make-docs-mkdocs: build-docs

make-docs: make-docs-pdoc make-docs-mkdocs

build-docs:
	@$(UV) run mkdocs build

# Self-documentation: use pydoc_fork to document itself
sample-docs:
	@$(UV) run python -m pydoc_fork pydoc_fork --output doc_self

sample-docs-dark:
	@$(UV) run python -m pydoc_fork pydoc_fork --output doc_self_dark --theme dark

dogfood: sample-docs sample-docs-dark
	@$(UV) run bash scripts/dogfood.sh

# ── Dead code analysis (advisory — non-blocking) ─────────────────────────────

dead-code: vulture deadcode

vulture:
	@echo "=== vulture (advisory) ==="
	@$(UV) run vulture $(PACKAGE) --min-confidence 80 || true

deadcode:
	@echo "=== deadcode (advisory) ==="
	@$(UV) run deadcode $(PACKAGE) || true

# ── Exploratory / advisory tools ─────────────────────────────────────────────

explore: refurb crosshair deptry import-linter

refurb:
	@echo "=== refurb: modern Python idiom suggestions (advisory) ==="
	@$(UV) run refurb $(PACKAGE) || true

crosshair:
	@echo "=== crosshair: symbolic execution / contract checking (advisory) ==="
	@$(UV) run crosshair check $(PACKAGE) || true

deptry:
	@echo "=== deptry: unused / missing / misplaced dependencies (advisory) ==="
	@$(UV) run deptry . || true

import-linter:
	@echo "=== import-linter: import architecture contracts (advisory) ==="
	@$(UV) run lint-imports || true

# ── Security ──────────────────────────────────────────────────────────────────

security: bandit audit

bandit:
	@$(UV) run bandit -q -c pyproject.toml -r $(PACKAGE)

audit:
	@echo "=== uv audit ==="
	@$(UV) audit --ignore-until-fixed PYSEC-2022-42969
	@echo "=== pip-audit ==="
	@$(UV) run pip-audit --ignore-vuln PYSEC-2022-42969

# ── Tests ─────────────────────────────────────────────────────────────────────

smoke:
	@$(UV) run bash scripts/basic_help.sh

test:
	@$(UV) run pytest --doctest-modules $(PACKAGE) -q
	@$(UV) run pytest -q \
		--cov=$(PACKAGE) \
		--cov-report=html \
		--junitxml=junit.xml \
		--timeout=60

test-ci:
	@$(UV) run pytest --doctest-modules $(PACKAGE) -q
	@$(UV) run pytest -q -n auto --dist=loadfile \
		--cov=$(PACKAGE) \
		--cov-report=xml \
		--junitxml=junit.xml \
		--timeout=60

tox:
	@$(UV) run tox

# ── Type checking ─────────────────────────────────────────────────────────────

typecheck: typecheck-mypy

typecheck-mypy:
	@$(UV) run mypy --hide-error-context --ignore-missing-imports $(PACKAGE)

# ── Metadata / version ───────────────────────────────────────────────────────

metadata:
	@$(UV) run metametameta pep621 --name $(PACKAGE) --source pyproject.toml --output $(ABOUT_FILE)
	@$(UV) run ruff check --fix --quiet $(ABOUT_FILE)
	@$(UV) run black --quiet $(ABOUT_FILE)

metadata-check:
	@$(UV) run metametameta sync-check --output __about__.py

version-check:
	@$(UV) run jiggle_version check

dev-status:
	@$(UV) run troml-dev-status validate .

# ── GitHub Actions maintenance ────────────────────────────────────────────────

gha-validate:
	@echo "Validating GitHub Actions workflows"
	@$(UV) run python -c "import pathlib, yaml; [yaml.safe_load(p.read_text(encoding='utf-8')) for p in pathlib.Path('$(GHA_WORKFLOWS)').glob('*.yml')]; print('YAML parse OK')"
	@$(UV) run python -c "\
from pathlib import Path; import yaml; \
data=yaml.safe_load(Path('$(GHA_WORKFLOWS)/publish_to_pypi.yml').read_text(encoding='utf-8')); \
build_steps=data['jobs']['build']['steps']; \
publish_steps=data['jobs']['pypi-publish']['steps']; \
up=next(s for s in build_steps if s.get('uses','').startswith('actions/upload-artifact@')); \
down=next(s for s in publish_steps if s.get('uses','').startswith('actions/download-artifact@')); \
assert up['with']['name']==down['with']['name']=='packages'; \
assert up['with']['path']==down['with']['path']=='dist/'; \
print('Artifact handoff OK:', up['uses'], '->', down['uses'])"
	@uvx zizmor --no-progress --no-exit-codes .

gha-pin:
	@echo "Pinning GitHub Actions to current commit SHAs"
	@$(UV) run python -c "import os, subprocess, sys; \
token=os.environ.get('GITHUB_TOKEN') or subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True).stdout.strip(); \
assert token, 'Set GITHUB_TOKEN or run: gh auth login'; \
env=dict(os.environ, GITHUB_TOKEN=token); \
raise SystemExit(subprocess.run(['gha-update'], env=env).returncode)"

gha-upgrade: gha-pin gha-validate
	@echo "GitHub Actions upgrade complete"

publish-gha:
	@echo "Dispatching GitHub Actions publish workflow"
	gh workflow run publish_to_pypi.yml --ref main

# ── Clean ─────────────────────────────────────────────────────────────────────

clean-pyc:
	@$(UV) run pyclean $(PACKAGE) test || true

clean-test:
	@rm -f .coverage || true
	@rm -f .coverage.* || true
	@rm -f junit.xml || true

clean: clean-pyc clean-test

# ── Release gates ─────────────────────────────────────────────────────────────

publish-check:
	@$(UV) build
	@echo "Distribution built — inspect dist/ before publishing."
	@ls -lh dist/

publish:
	@echo "Publishing via uv (set UV_PUBLISH_TOKEN or configure OIDC trusted publishing)"
	@$(UV) publish

check: format-check lint-check security test typecheck metadata-check version-check
	@echo "All checks passed."

check-ci: format-check lint-check security test-ci typecheck metadata-check version-check
	@echo "CI checks passed."

prerelease: check dev-status docs-check smoke spell publish-check
	@echo "Pre-release checks complete — ready to publish."

# LLM-friendly quiet variants
.PHONY: pytest-llm pylint-llm check-llm
pytest-llm:
	@$(UV) run pytest --doctest-modules $(PACKAGE) -q
	@$(UV) run pytest test -q -n auto --cov=$(PACKAGE) --cov-report=term-missing:skip-covered --cov-fail-under 60

pylint-llm:
	@$(UV) run ruff check --fix --quiet $(PACKAGE) || true
	@$(UV) run pylint $(PACKAGE) --fail-under 9.0 --reports=n --score=n --disable=C,R,W

check-llm: pytest-llm pylint-llm
	@echo "All LLM checks passed"

# ── Dogfooding targets (independent, not wired into check) ───────────────────

.PHONY: prerelease-check
prerelease-check: version-check dev-status
	@echo "Pre-release checks passed."

.PHONY: dont-be-lazy
dont-be-lazy:
	@$(UV) dont_be_lazy --root . --no-color summary
	@$(UV) dont_be_lazy --root . --no-color scan pydoc_fork --no-config-suppressions || true

# ── Dogfooding targets (independent, not wired into check) ───────────────────
