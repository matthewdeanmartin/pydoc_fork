# !/usr/bin/env python3
import inspect
from typing import Any, Tuple, Union

from pydoc_fork.html_generator import HTMLDoc
from pydoc_fork.ui_code import describe, locate
from pydoc_fork.utils import _getdoc

"""Generate Python documentation in HTML or text for interactive use.

At the Python interactive prompt, calling help(thing) on a Python object
documents the object, and calling help() starts up an interactive
help session.

Or, at the shell command line outside of Python:

Run "pydoc <name>" to show documentation on something.  <name> may be
the name of a function, module, package, or a dotted reference to a
class or function within a module or module in a package.  If the
argument contains a path segment delimiter (e.g. slash on Unix,
backslash on Windows) it is treated as the path to a Python source file.

Run "pydoc -k <keyword>" to search for a keyword in the synopsis lines
of all available modules.

Run "pydoc -n <hostname>" to start an HTTP server with the given
hostname (default: localhost) on the local machine.

Run "pydoc -p <port>" to start an HTTP server on the given port on the
local machine.  Port number 0 can be used to get an arbitrary unused port.

Run "pydoc -b" to start an HTTP server on an arbitrary unused port and
open a web browser to interactively browse documentation.  Combine with
the -n and -p options to control the hostname and port used.

Run "pydoc -w <name>" to write out the HTML documentation for a module
to a file named "<name>.html".

Module docs for core modules are assumed to be in

    https://docs.python.org/X.Y/library/

This can be overridden by setting the PYTHONDOCS environment variable
to a different URL or to a local directory containing the Library
Reference Manual pages.
"""
# __all__ = ['help']
__author__ = "Ka-Ping Yee <ping@lfw.org>"
__date__ = "26 February 2001"

__credits__ = """Guido van Rossum, for an excellent programming language.
Tommy Burnette, the original creator of manpy.
Paul Prescod, for all his work on onlinehelp.
Richard Chamberlain, for the first implementation of textdoc.
"""

# Known bugs that can't be fixed here:
#   - synopsis() cannot be prevented from clobbering existing
#     loaded modules.
#   - If the __file__ attribute on a module is a relative path and
#     the current directory is changed with os.chdir(), an incorrect
#     path will be displayed.


# --------------------------------------- interactive interpreter interface

html = HTMLDoc()


def resolve(thing: Union[str, Any], forceload: int = 0) -> Tuple[Any, str]:
    """Given an object or a path to an object, get the object and its name."""
    if isinstance(thing, str):
        object = locate(thing, forceload)
        if object is None:
            raise ImportError('''\
No Python documentation found for %r.
Use help() to get the interactive help utility.
Use help(str) for help on the str class.''' % thing)
        return object, thing
    else:
        name = getattr(thing, '__name__', None)
        return thing, name if isinstance(name, str) else None


def render_doc(thing, title='Python Library Documentation: %s', forceload=0,
               renderer=None):
    """Render text documentation, given an object or a path to an object."""
    object, name = resolve(thing, forceload)
    desc = describe(object)
    module = inspect.getmodule(object)
    if name and '.' in name:
        desc += ' in ' + name[:name.rfind('.')]
    elif module and module is not object:
        desc += ' in module ' + module.__name__

    if not (inspect.ismodule(object) or
            inspect.isclass(object) or
            inspect.isroutine(object) or
            inspect.isdatadescriptor(object) or
            _getdoc(object)):
        # If the passed object is a piece of data or an instance,
        # document its available methods instead of its value.
        if hasattr(object, '__origin__'):
            object = object.__origin__
        else:
            object = type(object)
            desc += ' object'
    return title % desc + '\n\n' + renderer.document(object, name)

# def doc(thing, title='Python Library Documentation: %s', forceload=0,
#         output=None):
#     """Display text documentation, given an object or a path to an object."""
#     try:
#         if output is None:
#             pager(render_doc(thing, title, forceload))
#         else:
#             output.write(render_doc(thing, title, forceload, plaintext))
#     except (ImportError, ErrorDuringImport) as value:
#         print(value)
