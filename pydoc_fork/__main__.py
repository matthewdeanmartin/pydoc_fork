# noinspection PyPep8
"""pydoc_fork
A fork of pydoc that is optimized for generating html documentation in a CI context

Usage:
  pydoc_fork <package>... [--output=<folder>] [options]
  pydoc_fork (-h | --help)
  pydoc_fork --version

Options:
  -h --help                    Show this screen.
  -v --version                 Show version.
  --quiet                      No printing or logging.
  --verbose                    Crank up the logging.
  --config <config>            pyproject.toml or other toml config.
  --document_internals         respect underscore or __all__ private
  --prefer_docs_python_org     link to python.org or generate own stdlib docs
"""

# TODO: implement this
#   pydoc_fork dot_notation <importable>... [--output=<folder>] [--document_internals]
#   pydoc_fork source_path <path>... [--output=<folder>] [--document_internals]

import logging
import sys

import docopt

from pydoc_fork import commands, settings
from pydoc_fork.settings import load_config

LOGGER = logging.getLogger(__name__)
LOGGERS = []


__version__ = "3.0.0"


def main() -> int:
    """Get the args object from command parameters"""
    arguments = docopt.docopt(__doc__, version=f"pydoc_fork {__version__}")
    config_path = arguments.get("<config>")
    if config_path:
        load_config(config_path)

    LOGGER.debug(f"Invoking with docopts: {str(arguments)}")
    output_folder = arguments["--output"]

    # TODO: add lists of packages
    package = arguments["<package>"] or []
    # quiet = bool(arguments.get("--quiet", False))
    if arguments.get("--document_internals"):
        settings.DOCUMENT_INTERNALS = arguments["--document_internals"]
    if arguments.get("--prefer_docs_python_org"):
        settings.PREFER_DOCS_PYTHON_ORG = arguments["--prefer_docs_python_org"]

    if arguments.get("--verbose"):
        # root logger, all modules
        for root in ("pydoc_fork", "__main__"):
            logger = logging.getLogger(root)
            logger.setLevel(logging.DEBUG)
            handler = logging.StreamHandler()
            handler.setLevel(logging.DEBUG)
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            formatter = logging.Formatter(log_format)
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            LOGGERS.append(logger)

    commands.process_path_or_dot_name(
        package,
        output_folder=output_folder,
    )
    # # TODO
    #     print("Don't recognize that command.")
    #     return -1
    return 0


if __name__ == "__main__":
    sys.exit(main())
