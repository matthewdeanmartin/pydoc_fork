# noinspection PyPep8
"""pydoc_fork
A fork of pydoc that is optimized for generating html documentation in a CI context

Usage:
  pydoc_fork <package>... [--output=<folder>] [--document_internals]
  pydoc_fork importable <importable>... [--output=<folder>] [--document_internals]
  pydoc_fork source <path>... [--output=<folder>] [--document_internals]
  pydoc_fork (-h | --help)
  pydoc_fork --version

Options:
  -h --help                    Show this screen.
  -v --version                 Show version.
  --quiet                      No printing or logging.
  --verbose                    Crank up the logging.
"""

import logging
import sys

import docopt

import pydoc_fork.commands as commands

LOGGER = logging.getLogger(__name__)
LOGGERS = []


__version__ = "3.0.0"


def main() -> int:
    """Get the args object from command parameters"""
    arguments = docopt.docopt(__doc__, version=f"so_pip {__version__}")
    LOGGER.debug(str(arguments))
    output_folder = arguments["--output"]

    # TODO: add lists of packages
    package = arguments["<package>"] or []
    # quiet = bool(arguments.get("--quiet", False))
    document_internals = arguments["--document_internals"]

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

    commands.cli(
        package, output_folder=output_folder, document_internals=document_internals
    )
    # # TODO
    #     print("Don't recognize that command.")
    #     return -1
    return 0


if __name__ == "__main__":
    sys.exit(main())
