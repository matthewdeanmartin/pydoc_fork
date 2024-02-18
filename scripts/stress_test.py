from test.test_live_generation import cwd

import importlib_metadata
import pkg_resources

from pydoc_fork import process_path_or_dot_name
from pydoc_fork.module_utils import ErrorDuringImport


def run():
    installed_packages = pkg_resources.working_set

    installed_modules = importlib_metadata.packages_distributions()
    with cwd("."):
        output_folder = "doc_all_installed"
        for package in installed_modules.items():
            # name=package.module_path +"/"+package.project_name +"/"
            # name = package.project_name
            package_name, names = package
            try:
                results = process_path_or_dot_name(
                    [package_name], output_folder=output_folder, document_internals=True
                )
            except ImportError:
                # module name != package name
                pass
            except ErrorDuringImport:
                pass
            assert results


if __name__ == "__main__":
    run()
