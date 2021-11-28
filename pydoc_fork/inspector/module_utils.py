"""
Module Manipulation
"""
import builtins

# noinspection PyProtectedMember
import importlib._bootstrap

# noinspection PyProtectedMember
import importlib._bootstrap_external
import importlib.machinery
import importlib.util
import logging
import os
import sys
from typing import Any, Dict, Optional, Tuple, cast

from pydoc_fork.inspector.custom_types import TypeLike

LOGGER = logging.getLogger(__name__)


class ImportTimeError(Exception):
    """Errors that occurred while trying to import something to document it."""

    def __init__(self, filename: Optional[str], exc_info: Tuple[Any, Any, Any]) -> None:
        self.filename = filename
        # pylint: disable=invalid-name
        self.exc, self.value, self.tb = exc_info

    def __str__(self) -> str:
        exc = self.exc.__name__
        return f"problem in {self.filename} - {exc}: {self.value}"


# noinspection PyProtectedMember
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
    except BaseException as import_error:
        LOGGER.warning(f"Skipping importfile for {name} at {path}, got a {import_error}")
        raise ImportTimeError(path, sys.exc_info()) from import_error


def safe_import(
    path: str,
    force_load: bool = False,
    cache: Dict[str, Any] = {},  # noqa - this is mutable on purpose!
) -> Any:
    """Import a module; handle errors; return None if the module isn't found.

    If the module *is* found but an exception occurs, it's wrapped in an
    ErrorDuringImport exception and reraised.  Unlike __import__, if a
    package path is specified, the module at the end of the path is returned,
    not the package at the beginning.  If the optional 'force_load' argument
    is True, we reload the module from disk (unless it's a dynamic extension)."""
    try:
        # If force_load is True and the module has been previously loaded from
        # disk, we always have to reload the module.  Checking the file's
        # mtime isn't good enough (e.g. the module could contain a class
        # that inherits from another module that has changed).
        if force_load and path in sys.modules:
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
    except BaseException as import_error:
        # Did the error occur before or after the module was found?
        (exc, value, _) = info = sys.exc_info()
        if path in sys.modules:
            # An error occurred while executing the imported module.
            LOGGER.warning(f"Skipping safe_import for {path}, got a {import_error}")
            raise ImportTimeError(sys.modules[path].__file__, info) from import_error
        if exc is SyntaxError:
            # A SyntaxError occurred before we could execute the module.
            # MR : this isn't null safe.
            LOGGER.warning(f"Skipping safe_import for {path}, got a {str(exc)}")
            raise ImportTimeError(
                cast(SyntaxError, value).filename, info
            ) from import_error
        if issubclass(exc, ImportError) and cast(ImportError, value).name == path:
            LOGGER.warning(f"Skipping safe_import for {path}, got a {import_error}")
            LOGGER.warning(f"Cannot import this path: {path}")
            # No such module in the path.
            return None
        LOGGER.warning(f"Skipping safe_import for {path}, got a {import_error}")
        # Some other error occurred during the importing process.
        raise ImportTimeError(path, sys.exc_info()) from import_error
    for part in path.split(".")[1:]:
        try:
            module = getattr(module, part)
        except AttributeError:
            LOGGER.warning(f"While safe_import - {str(module)} does not have {part} from dot path {path}")
            return None
    return module


def ispackage(path: str) -> bool:
    """Guess whether a path refers to a package directory."""
    if os.path.isdir(path):
        for ext in (".py", ".pyc"):
            if os.path.isfile(os.path.join(path, "__init__" + ext)):
                return True
    return False


def locate(path: str, force_load: bool = False) -> Any:
    """Locate an object by name or dotted path, importing as necessary."""
    if "-" in path:
        # Not sure about this
        path = path.replace("-", "_")

    LOGGER.debug(f"locate(): locating {path}")
    parts = [part for part in path.split(".") if part]

    module, index = None, 0
    while index < len(parts):
        next_module = safe_import(".".join(parts[: index + 1]), force_load)
        if next_module:
            module, index = next_module, index + 1
        else:
            break
    if module:
        the_object = module
        # this errors?!
        # LOGGER.debug(f"putative module {str(the_object)}")
    else:
        the_object = builtins

    for part in parts[index:]:
        try:
            the_object = getattr(the_object, part)
        except AttributeError:
            LOGGER.debug(f"locate(): Don't think this is a module {the_object}")
            return None
    return the_object
