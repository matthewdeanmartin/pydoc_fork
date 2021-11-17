"""
Module Manipulation
"""
import builtins
import importlib._bootstrap
import importlib._bootstrap_external
import importlib.machinery
import importlib.util
import os
import sys
from typing import Any, Dict, Tuple, cast

from pydoc_fork.custom_types import TypeLike


class ErrorDuringImport(Exception):
    """Errors that occurred while trying to import something to document it."""

    def __init__(self, filename: str, exc_info: Tuple[Any, Any, Any]) -> None:
        self.filename = filename
        self.exc, self.value, self.tb = exc_info

    def __str__(self) -> str:
        exc = self.exc.__name__
        return f"problem in {self.filename} - {exc}: {self.value}"


def importfile(path: str) -> TypeLike:
    """Import a Python source file or compiled file given its path."""
    magic = importlib.util.MAGIC_NUMBER
    with open(path, "rb") as file:
        is_bytecode = magic == file.read(len(magic))
    filename = os.path.basename(path)
    name, _ = os.path.splitext(filename)
    if is_bytecode:
        loader = importlib._bootstrap_external.SourcelessFileLoader(name, path)
    else:
        loader = importlib._bootstrap_external.SourceFileLoader(name, path)
    # XXX We probably don't need to pass in the loader here.
    spec = importlib.util.spec_from_file_location(name, path, loader=loader)
    try:
        return cast(TypeLike, importlib._bootstrap._load(spec))
    # pylint: disable=broad-except
    except BaseException:
        raise ErrorDuringImport(path, sys.exc_info())


def safe_import(
    path: str,
    forceload: int = 0,
    cache: Dict[str, Any] = {},  # noqa - this is mutable on purpose!
) -> Any:
    """Import a module; handle errors; return None if the module isn't found.

    If the module *is* found but an exception occurs, it's wrapped in an
    ErrorDuringImport exception and reraised.  Unlike __import__, if a
    package path is specified, the module at the end of the path is returned,
    not the package at the beginning.  If the optional 'forceload' argument
    is 1, we reload the module from disk (unless it's a dynamic extension)."""
    print(path)
    try:
        # If forceload is 1 and the module has been previously loaded from
        # disk, we always have to reload the module.  Checking the file's
        # mtime isn't good enough (e.g. the module could contain a class
        # that inherits from another module that has changed).
        if forceload and path in sys.modules:
            if path not in sys.builtin_module_names:
                # Remove the module from sys.modules and re-import to try
                # and avoid problems with partially loaded modules.
                # Also remove any submodules because they won't appear
                # in the newly loaded module's namespace if they're already
                # in sys.modules.
                subs = [m for m in sys.modules if m.startswith(path + ".")]
                for key in [path] + subs:
                    # Prevent garbage collection.
                    cache[key] = sys.modules[key]
                    del sys.modules[key]
        module = __import__(path)
    # pylint: disable=broad-except
    except BaseException:
        # Did the error occur before or after the module was found?
        (exc, value, _) = info = sys.exc_info()
        if path in sys.modules:
            # An error occurred while executing the imported module.
            raise ErrorDuringImport(sys.modules[path].__file__, info)
        if exc is SyntaxError:
            # A SyntaxError occurred before we could execute the module.
            # MR : this isn't null safe.
            raise ErrorDuringImport(value.filename, info)
        if issubclass(exc, ImportError) and value.name == path:
            # No such module in the path.
            return None
        # Some other error occurred during the importing process.
        raise ErrorDuringImport(path, sys.exc_info())
    for part in path.split(".")[1:]:
        try:
            module = getattr(module, part)
        except AttributeError:
            return None
    return module


def ispackage(path: str) -> bool:
    """Guess whether a path refers to a package directory."""
    if os.path.isdir(path):
        for ext in (".py", ".pyc"):
            if os.path.isfile(os.path.join(path, "__init__" + ext)):
                return True
    return False


def locate(path: str, forceload: int = 0) -> Any:
    """Locate an object by name or dotted path, importing as necessary."""
    print(f"locating {path}")
    parts = [part for part in path.split(".") if part]
    print(parts)
    module, index = None, 0
    while index < len(parts):
        nextmodule = safe_import(".".join(parts[: index + 1]), forceload)
        if nextmodule:
            module, index = nextmodule, index + 1
        else:
            break
    if module:
        the_object = module
        # this errors?!
        # print(f"putative module {str(the_object)}")
    else:
        the_object = builtins

    for part in parts[index:]:
        try:
            the_object = getattr(the_object, part)
        except AttributeError:
            print(f"Don't think this is a module {the_object}")
            return None
    return the_object
