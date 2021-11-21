"""
Just enough UI to let a build server generate documentation
"""
import logging
import os
import pkgutil
from typing import List, Optional, Union

import pydoc_fork.formatter_html as html
from pydoc_fork.custom_types import TypeLike
from pydoc_fork.format_page import render
from pydoc_fork.module_utils import ErrorDuringImport
from pydoc_fork.path_utils import _adjust_cli_sys_path
from pydoc_fork.utils import describe, resolve

LOGGER = logging.getLogger(__name__)


# MR output_folder
def writedoc(
    thing: Union[TypeLike, str],
    output_folder: str,
    document_internals: bool,
    forceload: int = 0,
) -> Optional[str]:
    """Write HTML documentation to a file in the current directory."""
    try:
        the_object, name = resolve(thing, forceload)

        # MR
        # should go in constructor, but what? no constructor
        html.OUTPUT_FOLDER = output_folder
        html.DOCUMENT_INTERNALS = document_internals
        page_out = render(describe(the_object), the_object, name)
        # MR output_folder + os.sep
        full_path = output_folder + os.sep + name + ".html"
        with open(full_path, "w", encoding="utf-8") as file:
            file.write(page_out)
        print("wrote", name + ".html")
        return full_path
    except (ImportError, ErrorDuringImport) as value:
        print(value)
    return ""


def write_docs_per_module(
    modules: List[str], output_folder: str, document_internals: bool
) -> List[str]:
    """Write out HTML documentation for all modules in a directory tree."""

    # This is going to handle filesystem paths, e.g. ./module/submodule.py
    # There will be ANOTHER method to handle MODULE paths, e.g. module.submodule"
    # Attempting to mix these two types is a bad idea.
    written: List[str] = []
    for module in modules:
        # file
        if module.lower().endswith(".py"):
            full_path = writedoc(module[:-3], output_folder, document_internals)
            written.append(full_path)
        else:
            # source folder
            full_path = writedoc(module, output_folder, document_internals)
            written.append(full_path)
            # "." needs to mean pwd... does it?
            full_paths = writedocs(
                ".", output_folder, document_internals, for_only=module
            )
            written.extend(full_paths)
    return written


def writedocs(
    source_directory: str,
    output_folder: str,
    document_internals: bool,
    for_only: str = "",
) -> List[str]:
    """Write out HTML documentation for all modules in a directory tree."""
    # if done is None: done = {}
    pkgpath = ""
    # walk packages is why pydoc drags along with it tests folders
    LOGGER.debug(f"Walking packages for {source_directory}")

    full_paths: List[str] = []
    for _, modname, _ in pkgutil.walk_packages([source_directory], pkgpath):
        if not str(modname).startswith(for_only):
            continue
        LOGGER.debug(f"docing {modname})")
        full_path = writedoc(modname, output_folder, document_internals)
        full_paths.append(full_path)
    return full_paths


def cli(
    files: List[str],
    # TODO source_folder,
    output_folder: str,
    document_internals: bool,
) -> List[str]:
    """Command-line interface (looks at sys.argv to decide what to do)."""
    LOGGER.debug(f"{files}, {output_folder}, {document_internals}")

    _adjust_cli_sys_path()

    # opts, args = getopt.getopt(sys.argv[1:], 'bk:n:p:w')
    return write_docs_per_module(files, output_folder, document_internals)
    # for file in files:
    #     if ispath(file) and not os.path.exists(file):
    #         print("file %r does not exist" % files)
    #         break
    #     try:
    #         # single file module
    #         if ispath(file) and os.path.isfile(file):
    #             # new type assigned to same name
    #             arg_type = importfile(file)
    #             writedoc(arg_type, output_folder, document_internals)
    #         # directory
    #         elif ispath(file) and os.path.isdir(file):
    #             print(f"We think this is a path & a directory 1")
    #
    #         elif (
    #             isinstance(files, str) and os.path.exists(files) and os.path.isdir(files)
    #         ):
    #             print(f"We think this is a path & a directory 2")
    #             write_docs_per_module(files, output_folder, document_internals)
    #         else:
    #             print(f"We think this is a built in or something on the PYTHONPATH")
    #             # built ins?
    #             write_docs_per_module(files, output_folder, document_internals)
    #             # raise TypeError("Not a file, not a directory")
    #
    #     except ErrorDuringImport as value:
    #         print(value)


if __name__ == "__main__":
    #     # cli([".\\"], output_folder=, document_internals=True)
    cli(["pydoc_fork"], output_folder="docs_api", document_internals=True)
#     # cli(["sys"], output_folder="docs_api", document_internals=False)
#     # cli(["cats"], output_folder="docs_api") # writes cats.html, even tho this isn't a module!
#     # cli(["inspect"], output_folder="docs_api", document_internals=False)
