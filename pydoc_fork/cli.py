"""Top-level `pydoc` CLI entry point.

Supports:
  pydoc gui              — launch the Tkinter GUI
  pydoc <package> ...    — generate HTML docs (same as pydoc_fork)
"""

import sys


def main() -> int:
    """Dispatch based on the first argument."""
    if len(sys.argv) > 1 and sys.argv[1] == "gui":
        from pydoc_fork.gui import main as gui_main

        gui_main()
        return 0

    from pydoc_fork.__main__ import main as fork_main

    return fork_main()


if __name__ == "__main__":
    sys.exit(main())
