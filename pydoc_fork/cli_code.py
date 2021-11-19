"""
Just enough UI to let a build server generate documentation
"""
import getopt
import logging
import os
import pkgutil
import sys
from typing import List, Union

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.formatter_html import HTMLDoc
from pydoc_fork.module_utils import ErrorDuringImport
from pydoc_fork.path_utils import _adjust_cli_sys_path
from pydoc_fork.utils import describe, resolve

LOGGER = logging.getLogger(__name__)
html = HTMLDoc()


# MR output_folder
def writedoc(
    thing: Union[TypeLike, str],
    output_folder: str,
    document_internals: bool,
    forceload: int = 0,
) -> None:
    """Write HTML documentation to a file in the current directory."""
    try:
        the_object, name = resolve(thing, forceload)

        # MR
        # should go in constructor, but what? no constructor
        html.output_folder = output_folder
        html.document_internals = document_internals
        page = html.page(
            describe(the_object), html.document(the_object, name, output_folder)
        )
        # MR output_folder + os.sep
        with open(
            output_folder + os.sep + name + ".html", "w", encoding="utf-8"
        ) as file:
            file.write(page)
        print("wrote", name + ".html")
    except (ImportError, ErrorDuringImport) as value:
        print(value)


def write_docs_per_module(
    modules: List[str], output_folder: str, document_internals: bool
) -> None:
    """Write out HTML documentation for all modules in a directory tree."""
    for module in modules:
        writedoc(module, output_folder, document_internals)
        # "." needs to mean pwd... does it?
        writedocs(".", output_folder, document_internals, for_only=module)


def writedocs(
    source_directory: str,
    output_folder: str,
    document_internals: bool,
    for_only: str = "",
) -> None:  # , pkgpath='', done=None): #ununsed args
    """Write out HTML documentation for all modules in a directory tree."""
    # if done is None: done = {}
    pkgpath = ""
    # walk packages is why pydoc drags along with it tests folders
    LOGGER.debug(f"Walking packages for {source_directory}")

    for _, modname, _ in pkgutil.walk_packages([source_directory], pkgpath):
        if not str(modname).startswith(for_only):
            continue
        LOGGER.debug(f"docing {modname})")
        writedoc(modname, output_folder, document_internals)


# -------------------------------------------------- command-line interface


def cli(
    files: List[str],
    # TODO source_folder,
    output_folder: str,
    document_internals: bool,
) -> None:
    """Command-line interface (looks at sys.argv to decide what to do)."""
    LOGGER.debug(files, output_folder, document_internals)

    class BadUsage(Exception):
        """Bad Usage"""

    _adjust_cli_sys_path()

    try:
        # opts, args = getopt.getopt(sys.argv[1:], 'bk:n:p:w')
        args = files
        if not args:
            raise BadUsage
        write_docs_per_module(files, output_folder, document_internals)
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

    except (getopt.error, BadUsage):
        cmd = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        print(
            """pydoc_forked - the Python documentation tool
{cmd} -w <name> ...
    Write out the HTML documentation for a module to a file in the current
    directory.  If <name> contains a '{sep}', it is treated as a filename; if
    it names a directory, documentation is written for all the contents.
""".format(
                cmd=cmd, sep=os.sep
            )
        )


if __name__ == "__main__":
    #     # cli([".\\"], output_folder=, document_internals=True)
    cli(["pydoc_fork"], output_folder="docs_api", document_internals=True)
#     # cli(["sys"], output_folder="docs_api", document_internals=False)
#     # cli(["cats"], output_folder="docs_api") # writes cats.html, even tho this isn't a module!
#     # cli(["inspect"], output_folder="docs_api", document_internals=False)
