import sysconfig
import datetime

import sys

from pydoc_fork.format_module import getdocloc


def test_getdocloc_datetime():
    STDLIB_BASEDIR = sysconfig.get_path("stdlib")
    # PYTHONDOCS = os.environ.get(
    #     "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
    # )
    result = getdocloc(datetime, STDLIB_BASEDIR)
    print(result)
    assert "https://docs.python.org/3.9/library/datetime.html" in result


def test_getdocloc_sys():
    STDLIB_BASEDIR = sysconfig.get_path("stdlib")
    # PYTHONDOCS = os.environ.get(
    #     "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
    # )
    result = getdocloc(sys, STDLIB_BASEDIR)
    print(result)
    assert "https://docs.python.org/3.9/library/sys.html" in result
