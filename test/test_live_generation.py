import os

from pydoc_fork import cli


from contextlib import contextmanager

# https://stackoverflow.com/a/37996581/33264
from pydoc_fork.module_utils import ErrorDuringImport


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
        results = cli(
            ["navio_tasks"], output_folder=output_folder, document_internals=True
        )
        results = cli(
            ["pydoc_fork"], output_folder=output_folder, document_internals=True
        )
        assert results
        results = cli(
            ["pydoc_fork//pydoc_fork"],
            output_folder=output_folder,
            document_internals=True,
        )
        assert results
        results = cli(
            ["test.pydocfodder"], output_folder=output_folder, document_internals=True
        )
        assert results
        results = cli(
            ["test.pydoc_mod"], output_folder=output_folder, document_internals=True
        )
        assert results
        #  can't do this yet, pydoc stills imports each module!
        # cli([".\\"], output_folder=".", document_internals=True)
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
