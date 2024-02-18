import os
from contextlib import contextmanager

from pydoc_fork import process_path_or_dot_name

# https://stackoverflow.com/a/37996581/33264
from pydoc_fork.inspector.module_utils import ImportTimeError


@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_cli():
    with cwd("."):
        output_folder = "doc_self"
        results = process_path_or_dot_name(
            ["navio_tasks"],
            output_folder=output_folder,
        )
        results = process_path_or_dot_name(
            ["pydoc_fork"],
            output_folder=output_folder,
        )
        assert results
        results = process_path_or_dot_name(
            ["test.pydocfodder"],
            output_folder=output_folder,
        )
        assert results
        results = process_path_or_dot_name(
            ["test.pydoc_mod"],
            output_folder=output_folder,
        )
        assert results
        #  can't do this yet, pydoc stills imports each module!
        # process_path_or_dot_name([".\\"], output_folder=".", document_internals=True)
        try:
            files_in_directory = os.listdir(".")
            filtered_files = [
                file for file in files_in_directory if file.endswith(".html")
            ]
            for file in filtered_files:
                path_to_file = os.path.join(".", file)
                os.remove(path_to_file)
        except:
            pass
