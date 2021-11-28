import sys

import pydoc_fork.inspector.path_utils as path_utils


def test_get_revised_path():
    python_path = sys.path.copy()
    new_python_path = path_utils._get_revised_path(python_path, ".")
    if new_python_path and python_path:
        assert len(new_python_path) > len(python_path)
