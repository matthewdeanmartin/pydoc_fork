import os

from pydoc_fork import cli


from contextlib import contextmanager

# https://stackoverflow.com/a/37996581/33264
@contextmanager
def cwd(path):
    oldpwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(oldpwd)


def test_cli():
    with cwd("../"):
        cli(["pydoc_fork//pydoc_fork"], output_folder=".", document_internals=True)
        cli(["pydocfodder"], output_folder=".", document_internals=True)
        cli(["pydoc_mod"], output_folder=".", document_internals=True)
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
