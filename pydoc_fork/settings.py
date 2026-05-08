"""
Configuration options that could be used by anything.

Also global variables
"""

import logging
import os
import pathlib
import sys
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

LOGGER = logging.getLogger(__name__)
# pylint: disable=global-statement
MENTIONED_MODULES: set[tuple[Any, str]] = set()
SKIP_MODULES = ["typing"]
PREFER_DOCS_PYTHON_ORG = False
DOCUMENT_INTERNALS = False
ONLY_NAMED_AND_SUBS = False
GENERATE_INDEX = True
PROJECT_NAME = "Python Project"

OUTPUT_FOLDER = ""
THEME = "classic"
CUSTOM_TEMPLATES: str | None = None

PYTHONDOCS = os.environ.get(
    "PYTHONDOCS", f"https://docs.python.org/{sys.version_info[0]}.{sys.version_info[1]}/library"
)
"""Module docs for core modules are assumed to be in

    https://docs.python.org/X.Y/library/

This can be overridden by setting the PYTHONDOCS environment variable
to a different URL or to a local directory containing the Library
Reference Manual pages."""


def load_config(path: str | None):
    """Copy config from toml to globals"""
    global PREFER_DOCS_PYTHON_ORG
    global DOCUMENT_INTERNALS
    global SKIP_MODULES
    global ONLY_NAMED_AND_SUBS
    global THEME
    global CUSTOM_TEMPLATES
    global GENERATE_INDEX
    global PROJECT_NAME

    pairs = parse_toml(path)
    if pairs:
        LOGGER.debug("Found config at %s", path)
    PREFER_DOCS_PYTHON_ORG = pairs.get("PREFER_DOCS_PYTHON_ORG", False)
    DOCUMENT_INTERNALS = pairs.get("DOCUMENT_INTERNALS", True)
    SKIP_MODULES = pairs.get("SKIP_MODULES", ["typing"])
    ONLY_NAMED_AND_SUBS = pairs.get("ONLY_NAMED_AND_SUBS", False)
    THEME = pairs.get("THEME", "classic")
    CUSTOM_TEMPLATES = pairs.get("CUSTOM_TEMPLATES", None)
    GENERATE_INDEX = pairs.get("GENERATE_INDEX", True)
    PROJECT_NAME = pairs.get("PROJECT_NAME", "Python Project")


def parse_toml(path_string: str | None) -> dict[str, Any]:
    """Parse toml"""
    path = pathlib.Path(os.getcwd()) if not path_string else pathlib.Path(path_string)
    toml_path = path / "pyproject.toml"
    if not toml_path.exists():
        return {}
    with open(toml_path, "rb") as handle:
        pyproject_toml = tomllib.load(handle)
    config = pyproject_toml.get("tool", {}).get("pydoc_fork", {})
    loose_matching = {k.replace("--", "").replace("-", "_"): v for k, v in config.items()}
    return loose_matching
