"""
Path Manipulation
"""
import logging
import os
import sys
from typing import List, Optional

LOGGER = logging.getLogger(__name__)


def _get_revised_path(
    current_python_path: List[str], script_path: str
) -> Optional[List[str]]:
    """Ensures current directory is on returned path, and argv0 directory is not

    Exception: argv0 dir is left alone if it's also pydoc's directory.

    Returns a new path entry list, or None if no adjustment is needed.
    """
    # Scripts may get the current directory in their path by default if they're
    # run with the -m switch, or directly from the current directory.
    # The interactive prompt also allows imports from the current directory.

    # Accordingly, if the current directory is already present, don't make
    # any changes to the given_path
    if (
        "" in current_python_path
        or os.curdir in current_python_path
        or os.getcwd() in current_python_path
    ):
        return None

    # Otherwise, add the current directory to the given path, and remove the
    # script directory (as long as the latter isn't also pydoc's directory.
    stdlib_dir = os.path.dirname(__file__)
    script_dir = os.path.dirname(script_path)
    revised_path = current_python_path.copy()
    if script_dir in current_python_path and not os.path.samefile(
        script_dir, stdlib_dir
    ):
        revised_path.remove(script_dir)
    revised_path.insert(0, os.getcwd())
    return revised_path


# Note: the tests only cover _get_revised_path, not _adjust_cli_path itself
def _adjust_cli_sys_path() -> None:
    """Ensures current directory is on sys.path, and __main__ directory is not.

    Exception: __main__ dir is left alone if it's also pydoc's directory.
    """
    revised_path = _get_revised_path(sys.path, sys.argv[0])
    if revised_path is not None:
        sys.path[:] = revised_path


def locate_file(file_name: str, executing_file: str) -> str:
    """
    Find file relative to a source file, e.g.
    locate_file("foo/bar.txt", __file__)

    Succeeds regardless to context of execution
    """
    file_path = os.path.join(
        os.path.dirname(os.path.abspath(executing_file)), file_name
    )
    return file_path
