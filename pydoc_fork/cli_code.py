import os
import pkgutil
import sys
import warnings

from pydoc_fork.main import html, resolve
from pydoc_fork.module_scanner_class import ModuleScanner
from pydoc_fork.ui_code import describe
from pydoc_fork.utils import ErrorDuringImport, importfile


def writedoc(thing, forceload=0):
    """Write HTML documentation to a file in the current directory."""
    try:
        object, name = resolve(thing, forceload)
        page = html.page(describe(object), html.document(object, name))
        with open(name + '.html', 'w', encoding='utf-8') as file:
            file.write(page)
        print('wrote', name + '.html')
    except (ImportError, ErrorDuringImport) as value:
        print(value)


def writedocs(dir, pkgpath='', done=None):
    """Write out HTML documentation for all modules in a directory tree."""
    if done is None: done = {}
    for importer, modname, ispkg in pkgutil.walk_packages([dir], pkgpath):
        writedoc(modname)
    return


def apropos(key):
    """Print all the one-line module summaries that contain a substring."""

    def callback(path, modname, desc):
        if modname[-9:] == '.__init__':
            modname = modname[:-9] + ' (package)'
        print(modname, desc and '- ' + desc)

    def onerror(modname):
        pass

    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')  # ignore problems during import
        ModuleScanner().run(callback, key, onerror=onerror)


# -------------------------------------------------- command-line interface

def ispath(x):
    return isinstance(x, str) and x.find(os.sep) >= 0


def _get_revised_path(given_path, argv0):
    """Ensures current directory is on returned path, and argv0 directory is not

    Exception: argv0 dir is left alone if it's also pydoc's directory.

    Returns a new path entry list, or None if no adjustment is needed.
    """
    # Scripts may get the current directory in their path by default if they're
    # run with the -m switch, or directly from the current directory.
    # The interactive prompt also allows imports from the current directory.

    # Accordingly, if the current directory is already present, don't make
    # any changes to the given_path
    if '' in given_path or os.curdir in given_path or os.getcwd() in given_path:
        return None

    # Otherwise, add the current directory to the given path, and remove the
    # script directory (as long as the latter isn't also pydoc's directory.
    stdlib_dir = os.path.dirname(__file__)
    script_dir = os.path.dirname(argv0)
    revised_path = given_path.copy()
    if script_dir in given_path and not os.path.samefile(script_dir, stdlib_dir):
        revised_path.remove(script_dir)
    revised_path.insert(0, os.getcwd())
    return revised_path


# Note: the tests only cover _get_revised_path, not _adjust_cli_path itself
def _adjust_cli_sys_path():
    """Ensures current directory is on sys.path, and __main__ directory is not.

    Exception: __main__ dir is left alone if it's also pydoc's directory.
    """
    revised_path = _get_revised_path(sys.path, sys.argv[0])
    if revised_path is not None:
        sys.path[:] = revised_path


def cli(files):
    """Command-line interface (looks at sys.argv to decide what to do)."""
    import getopt
    class BadUsage(Exception):
        pass

    _adjust_cli_sys_path()

    try:
        # opts, args = getopt.getopt(sys.argv[1:], 'bk:n:p:w')
        args = files
        if not args: raise BadUsage
        for arg in args:
            if ispath(arg) and not os.path.exists(arg):
                print('file %r does not exist' % arg)
                break
            try:
                if ispath(arg) and os.path.isfile(arg):
                    arg = importfile(arg)

                if ispath(arg) and os.path.isdir(arg):
                    writedocs(arg)
                else:
                    writedoc(arg)

            except ErrorDuringImport as value:
                print(value)

    except (getopt.error, BadUsage):
        cmd = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        print("""pydoc_forked - the Python documentation tool
{cmd} -w <name> ...
    Write out the HTML documentation for a module to a file in the current
    directory.  If <name> contains a '{sep}', it is treated as a filename; if
    it names a directory, documentation is written for all the contents.
""".format(cmd=cmd, sep=os.sep))


if __name__ == '__main__':
    cli([".\\"])
