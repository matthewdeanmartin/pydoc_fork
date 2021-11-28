"""
Configuration options that could be used by anything.

Also global variables
"""
import logging
import os
import pathlib
import sys
from typing import Any, Dict, Optional, Set, Tuple

import tomli

from pydoc_fork.inspector.custom_types import TypeLike

LOGGER = logging.getLogger(__name__)
# pylint: disable=global-statement
MENTIONED_MODULES: Set[Tuple[TypeLike, str]] = set()
SKIP_MODULES = ["typing"]
PREFER_DOCS_PYTHON_ORG = False
DOCUMENT_INTERNALS = False
ONLY_NAMED_AND_SUBS = False

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
    global PREFER_DOCS_PYTHON_ORG
    global DOCUMENT_INTERNALS
    global SKIP_MODULES
    global ONLY_NAMED_AND_SUBS

    pairs = parse_toml(path)
    if pairs:
        LOGGER.debug(f"Found config at {path}")
    PREFER_DOCS_PYTHON_ORG = pairs.get("PREFER_DOCS_PYTHON_ORG", False)
    DOCUMENT_INTERNALS = pairs.get("DOCUMENT_INTERNALS", True)
    SKIP_MODULES = pairs.get("SKIP_MODULES", ["typing"])
    ONLY_NAMED_AND_SUBS= pairs.get("ONLY_NAMED_AND_SUBS", False)

def parse_toml(path_string: Optional[str]) -> Dict[str, Any]:
    """Parse toml"""
    if not path_string:
        path = pathlib.Path(os.getcwd())
    else:
        path = pathlib.Path(path_string)
    toml_path = path / "pyproject.toml"
    if not toml_path.exists():
        return {}
    with open(toml_path, encoding="utf8") as handle:
        pyproject_toml = tomli.loads(handle.read())
    config = pyproject_toml.get("tool", {}).get("pydoc_fork", {})
    loose_matching = {
        k.replace("--", "").replace("-", "_"): v for k, v in config.items()
    }
    return loose_matching
