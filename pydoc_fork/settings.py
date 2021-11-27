"""
Configuration options that could be used by anything.
"""
import logging
import os
import pathlib
import sys
from typing import Any, Dict, Optional

import tomli

LOGGER = logging.getLogger(__name__)

SKIP_TYPING = True
SKIP_MODULES = ["typing"]
PREFER_DOCS_PYTHON_ORG = False
DOCUMENT_INTERNALS = False
OUTPUT_FOLDER = ""

PYTHONDOCS = os.environ.get(
    "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
)
"""Module docs for core modules are assumed to be in

    https://docs.python.org/X.Y/library/

This can be overridden by setting the PYTHONDOCS environment variable
to a different URL or to a local directory containing the Library
Reference Manual pages."""


def load_config(path: Optional[str]):
    """Copy config from toml to globals"""
    global SKIP_TYPING
    global PREFER_DOCS_PYTHON_ORG
    global DOCUMENT_INTERNALS
    global SKIP_MODULES

    pairs = parse_toml(path)
    if pairs:
        LOGGER.debug(f"Found config at {path}")
    SKIP_TYPING = pairs.get("SKIP_TYPING", True)
    PREFER_DOCS_PYTHON_ORG = pairs.get("PREFER_INTERNET_DOCUMENTATION", False)
    DOCUMENT_INTERNALS = pairs.get("DOCUMENT_INTERNALS", True)
    SKIP_MODULES = pairs.get("SKIP_MODULES", ["typing"])


def parse_toml(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        path = pathlib.Path(os.getcwd())
    toml_path = path / "pyproject.toml"
    if not toml_path.exists():
        return {}
    with open(toml_path, encoding="utf8") as f:
        pyproject_toml = tomli.loads(f.read())
    config = pyproject_toml.get("tool", {}).get("pydoc_fork", {})
    loose_matching = {
        k.replace("--", "").replace("-", "_"): v for k, v in config.items()
    }
    return loose_matching
