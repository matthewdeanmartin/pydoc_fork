from unittest.mock import patch

import pydoc_fork.__main__ as main


def test_process_docopts():
    anything = {
        "<package>": None,  # "pydoc_fork",
        "--output": "/tmp",
        "--document_internals": True,
        "--quiet": False,
        "--verbose": True,
    }
    with patch("docopt.docopt", return_value=anything) as mock:
        main.main()
