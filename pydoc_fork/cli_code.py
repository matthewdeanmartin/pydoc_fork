import os
import pkgutil
import sys
from typing import Any

from pydoc_fork.formatter_html import HTMLDoc
from pydoc_fork.module_utils import ErrorDuringImport, importfile
from pydoc_fork.path_utils import _adjust_cli_sys_path, ispath
from pydoc_fork.utils import describe, resolve

html = HTMLDoc()


# MR output_folder
def writedoc(
    thing: Any, output_folder: str, document_internals: bool, forceload: int = 0
) -> None:
    """Write HTML documentation to a file in the current directory."""
    try:
        object, name = resolve(thing, forceload)

        # MR
        # should go in constructor, but what? no constructor
        html.output_folder = output_folder
        html.document_internals = document_internals
        page = html.page(describe(object), html.document(object, name, output_folder))
        # MR output_folder + os.sep
        with open(
            output_folder + os.sep + name + ".html", "w", encoding="utf-8"
        ) as file:
            file.write(page)
        print("wrote", name + ".html")
    except (ImportError, ErrorDuringImport) as value:
        print(value)


def writedocs(
    dir: str, output_folder: str, document_internals: bool
) -> None:  # , pkgpath='', done=None): #ununsed args
    """Write out HTML documentation for all modules in a directory tree."""
    # if done is None: done = {}
    pkgpath = ""
    # walk packages is why pydoc drags along with it tests folders
    for importer, modname, ispkg in pkgutil.walk_packages([dir], pkgpath):
        writedoc(modname, output_folder, document_internals)


# -------------------------------------------------- command-line interface


def cli(files: list[str], output_folder: str, document_internals: bool) -> None:
    """Command-line interface (looks at sys.argv to decide what to do)."""
    import getopt

    class BadUsage(Exception):
        pass

    _adjust_cli_sys_path()

    try:
        # opts, args = getopt.getopt(sys.argv[1:], 'bk:n:p:w')
        args = files
        if not args:
            raise BadUsage
        for arg in args:
            if ispath(arg) and not os.path.exists(arg):
                print("file %r does not exist" % arg)
                break
            try:
                # single file module
                if ispath(arg) and os.path.isfile(arg):
                    arg = importfile(arg)
                    writedoc(arg, output_folder, document_internals)
                # directory
                elif ispath(arg) and os.path.isdir(arg):
                    # writedocs(arg, output_folder)
                    writedocs(arg, output_folder, document_internals)
                elif (
                    isinstance(arg, str) and os.path.exists(arg) and os.path.isdir(arg)
                ):
                    writedocs(arg, output_folder, document_internals)
                else:
                    # built ins?
                    writedoc(arg, output_folder, document_internals)
                    # raise TypeError("Not a file, not a directory")

            except ErrorDuringImport as value:
                print(value)

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
    cli([".\\"], output_folder="docs", document_internals=True)
    cli(["pydoc_fork"], output_folder="docs", document_internals=True)
    cli(["sys"], output_folder="docs", document_internals=False)
    # cli(["cats"], output_folder="docs") # writes cats.html, even tho this isn't a module!
    cli(["inspect"], output_folder="docs", document_internals=False)
