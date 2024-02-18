import datetime
import sys
import sysconfig

from pydoc_fork import settings
from pydoc_fork.reporter.format_module import getdocloc


def test_getdocloc_datetime():
    old = settings.PREFER_DOCS_PYTHON_ORG
    settings.PREFER_DOCS_PYTHON_ORG = True
    STDLIB_BASEDIR = sysconfig.get_path("stdlib")
    # PYTHONDOCS = os.environ.get(
    #     "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
    # )
    result = getdocloc(datetime, STDLIB_BASEDIR)
    print(result)
    assert result.startswith("https://docs.python.org/") and result.endswith(
        "/library/datetime.html"
    )
    settings.PREFER_DOCS_PYTHON_ORG = old


def test_getdocloc_sys():
    old = settings.PREFER_DOCS_PYTHON_ORG
    settings.PREFER_DOCS_PYTHON_ORG = True
    STDLIB_BASEDIR = sysconfig.get_path("stdlib")
    # PYTHONDOCS = os.environ.get(
    #     "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
    # )
    result = getdocloc(sys, STDLIB_BASEDIR)
    print(result)
    assert result.startswith("https://docs.python.org/") and result.endswith(
        "/library/sys.html"
    )
    settings.PREFER_DOCS_PYTHON_ORG = old
