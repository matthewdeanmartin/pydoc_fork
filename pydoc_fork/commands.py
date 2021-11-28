"""
Process commands as pure python functions.

All the CLI logic should be handled in __main__.
"""
import logging
import os
import pkgutil
from shutil import copy2
from typing import List, Optional, Union

from pydoc_fork import settings
from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.module_utils import ImportTimeError
from pydoc_fork.inspector.path_utils import _adjust_cli_sys_path, locate_file
from pydoc_fork.inspector.utils import describe, resolve
from pydoc_fork.reporter.format_page import render

LOGGER = logging.getLogger(__name__)


def document_one(
    thing: Union[TypeLike, str],
    output_folder: str,
    force_load: bool = False,
) -> Optional[str]:
    """Write HTML documentation to a file in the current directory."""
    try:
        the_object, name = resolve(thing, force_load)
    except (ImportError, ImportTimeError):
        LOGGER.warning(f"document_one failed for {str(thing)} with folder {output_folder}")
        return None

    # MR
    # should go in constructor, but what? no constructor
    settings.OUTPUT_FOLDER = output_folder
    page_out = render(describe(the_object), the_object, name)
    # MR output_folder + os.sep
    full_path = calculate_file_name(name, output_folder)

    with open(full_path, "w", encoding="utf-8") as file:
        file.write(page_out)
    print("wrote", name + ".html")
    return full_path
    # except (ImportError, ErrorDuringImport) as value:
    #     print(value)
    # return ""


def calculate_file_name(name: str, output_folder: str) -> str:
    """If this was written, what would its name be"""
    name = (
        name.replace("<", "")
        .replace(">", "")
        .replace(":", "")
        .replace(",", "_")
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
    )
    full_path = output_folder + os.sep + name + ".html"

    return full_path


def write_docs_per_module(
    modules: List[str],
    output_folder: str,
    skip_if_written: bool = False,
) -> List[str]:
    """Write out HTML documentation for all modules in a directory tree."""

    # This is going to handle filesystem paths, e.g. ./module/submodule.py
    # There will be ANOTHER method to handle MODULE paths, e.g. module.submodule"
    # Attempting to mix these two types is a bad idea.
    written: List[str] = []
    for module in modules:
        # file

        if module.lower().endswith(".py"):
            full_path = document_one(module[:-3], output_folder)
            if full_path:
                written.append(full_path)
        else:
            full_path = document_one(module, output_folder)
            if full_path:
                written.append(full_path)
            # "." needs to mean pwd... does it?
            full_paths = document_directory(".", output_folder, for_only=module)
            written.extend(full_paths)
    # One pass, not ready to walk entire tree.

    third_party_written = write_docs_live_module(output_folder, 0, skip_if_written)
    written.extend(third_party_written)
    return written


def write_docs_live_module(
    output_folder: str,
    total_third_party: int = 0,
    skip_if_written: bool = False,
) -> List[str]:
    """Write out HTML documentation for all modules in a directory tree."""

    # This is going to handle filesystem paths, e.g. ./module/submodule.py
    # There will be ANOTHER method to handle MODULE paths, e.g. module.submodule"
    # Attempting to mix these two types is a bad idea.
    written: List[str] = []
    while settings.MENTIONED_MODULES and total_third_party <= 100:
        module = settings.MENTIONED_MODULES.pop()
        thing, name = module  # destructure it
        # should only be live modules or dot notation modules, not paths.
        full_path = calculate_file_name(name, output_folder)
        if os.path.exists(full_path) and skip_if_written:
            settings.MENTIONED_MODULES.discard(module)
        else:
            actual_full_path = document_one(thing, output_folder)
            total_third_party += 1
            if actual_full_path:
                written.append(actual_full_path)
            settings.MENTIONED_MODULES.discard(module)

    # TODO: make this a param
    return written


def document_directory(
    source_directory: str,
    output_folder: str,
    for_only: str = "",
) -> List[str]:
    """Write out HTML documentation for all modules in a directory tree."""
    package_path = ""
    # walk packages is why pydoc drags along with it tests folders
    LOGGER.debug(f"document_directory: Walking packages for {source_directory}")

    full_paths: List[str] = []
    for _, modname, _ in pkgutil.walk_packages([source_directory], package_path):
        if not str(modname).startswith(for_only):
            continue
        LOGGER.debug(f"document_directory: current module: {modname})")
        full_path = document_one(modname, output_folder)
        if full_path:
            full_paths.append(full_path)
    return full_paths


def process_path_or_dot_name(
    files: List[str],
    output_folder: str,
    overwrite_existing: bool = False,
) -> List[str]:
    """
    Generate html documentation for all modules found at paths or
    dot notation module names.

    Args:
        files:
        output_folder:
        overwrite_existing:

    Returns:
        List of successfully documented modules
    """
    LOGGER.debug(f"process_path_or_dot_name for {files} and writing to {output_folder}")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    copy2(locate_file("templates/style.css", __file__), output_folder)

    _adjust_cli_sys_path()

    return write_docs_per_module(
        files, output_folder, skip_if_written=not overwrite_existing
    )


if __name__ == "__main__":
    process_path_or_dot_name([".\\"], output_folder="docs_api")
    process_path_or_dot_name(["pydoc_fork"], output_folder="docs_api")
    process_path_or_dot_name(["sys"], output_folder="docs_api")
    process_path_or_dot_name(
        ["cats"], output_folder="docs_api"
    )  # writes cats.html, even tho this isn't a module!
    process_path_or_dot_name(["inspect"], output_folder="docs_api")
