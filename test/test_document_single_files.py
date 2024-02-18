import os
import tempfile

import pytest

from pydoc_fork import process_path_or_dot_name
from pydoc_fork.inspector.path_utils import locate_file

# def test_single_file_pydoc_mod():
#     with tempfile.TemporaryDirectory(prefix="test_pydoc_mod") as directory:
#         folder_path = directory.replace("\\", "/")
#         results = process_path_or_dot_name(
#             ["test.pydoc_mod"], output_folder=folder_path,
#         )
#         print(results)
#         print(folder_path)
#         with open(
#             os.path.join(folder_path, "test.pydoc_mod.html"), encoding="utf-8"
#         ) as result:
#             html = result.read()
#             assert "Data descriptors defined here" in html
#         print()


@pytest.mark.skip(reason="Fails if output drive differs from temp drive")
def test_single_file_pydocfodder():
    with tempfile.TemporaryDirectory(prefix="pydoc_fodder") as directory:
        folder_path = directory.replace("\\", "/")
        results = process_path_or_dot_name(
            ["test.pydocfodder"],
            output_folder=folder_path,
        )
        print(results)
        print(folder_path)
        with open(
            os.path.join(folder_path, "test.pydocfodder.html"), encoding="utf-8"
        ) as result:
            html = result.read()
            assert "Python: module test.pydocfodder" in html
        print()


# def test_single_file_pydoc_mod_as_dot_py():
#     with tempfile.TemporaryDirectory(prefix="test_pydoc_mod") as directory:
#         folder_path = directory.replace("\\", "/")
#         # file_name = locate_file("pydocfodder.py", __file__)
#         file_name = "test.pydoc_mod"
#         results = process_path_or_dot_name([file_name], output_folder=folder_path,)
#         print(results)
#         print(folder_path)
#         with open(
#             os.path.join(folder_path, "test.pydoc_mod.html"), encoding="utf-8"
#         ) as result:
#             html = result.read()
#             assert "Data descriptors defined here" in html
#         print()


@pytest.mark.skip(reason="Fails if output drive differs from temp drive")
def test_single_file_pydocfodder_as_dot_py():
    # file_name = locate_file("pydocfodder.py", __file__)
    file_name = "test.pydocfodder"
    with tempfile.TemporaryDirectory(prefix="pydoc_fodder") as directory:
        folder_path = directory.replace("\\", "/")
        process_path_or_dot_name(
            [file_name],
            output_folder=folder_path,
        )
        print(folder_path)
        with open(
            os.path.join(folder_path, "test.pydocfodder.html"), encoding="utf-8"
        ) as result:
            html = result.read()
            assert "Python: module test.pydocfodder" in html
        print()
