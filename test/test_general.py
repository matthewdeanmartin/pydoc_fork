import contextlib
import importlib.util
import inspect
import os
import pkgutil
import py_compile
import re
import tempfile
import unittest
import urllib.parse

import sys

import pydoc_fork as pydoc
import test.support
from test import pydoc_mod
from test.support import import_helper
from test.support import os_helper
from test.support import reap_children, requires_docstrings
from test.support import threading_helper
from test.support.os_helper import TESTFN, rmtree, unlink
from test.support.script_helper import assert_python_ok, assert_python_failure


class nonascii:
    "Це не латиниця"
    pass


if test.support.HAVE_DOCSTRINGS:
    expected_data_docstrings = (
        "dictionary for instance variables (if defined)",
        "list of weak references to the object (if defined)",
    ) * 2
else:
    expected_data_docstrings = ("", "", "", "")

expected_text_pattern = """
NAME
    test.pydoc_mod - This is a test module for test_pydoc
%s
CLASSES
    builtins.object
        A
        B
        C
\x20\x20\x20\x20
    class A(builtins.object)
     |  Hello and goodbye
     |\x20\x20
     |  Methods defined here:
     |\x20\x20
     |  __init__()
     |      Wow, I have no function!
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__%s
     |\x20\x20
     |  __weakref__%s
\x20\x20\x20\x20
    class B(builtins.object)
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__%s
     |\x20\x20
     |  __weakref__%s
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data and other attributes defined here:
     |\x20\x20
     |  NO_MEANING = 'eggs'
     |\x20\x20
     |  __annotations__ = {'NO_MEANING': <class 'str'>}
\x20\x20\x20\x20
    class C(builtins.object)
     |  Methods defined here:
     |\x20\x20
     |  get_answer(self)
     |      Return say_no()
     |\x20\x20
     |  is_it_true(self)
     |      Return self.get_answer()
     |\x20\x20
     |  say_no(self)
     |\x20\x20
     |  ----------------------------------------------------------------------
     |  Data descriptors defined here:
     |\x20\x20
     |  __dict__
     |      dictionary for instance variables (if defined)
     |\x20\x20
     |  __weakref__
     |      list of weak references to the object (if defined)

FUNCTIONS
    doc_func()
        This function solves all of the world's problems:
        hunger
        lack of Python
        war
\x20\x20\x20\x20
    nodoc_func()

DATA
    __xyz__ = 'X, Y and Z'

VERSION
    1.2.3.4

AUTHOR
    Benjamin Peterson

CREDITS
    Nobody

FILE
    %s
""".strip()

expected_text_data_docstrings = tuple(
    "\n     |      " + s if s else "" for s in expected_data_docstrings
)

html2text_of_expected = """
test.pydoc_mod (version 1.2.3.4)
This is a test module for test_pydoc

Classes
    builtins.object
    A
    B
    C

class A(builtins.object)
    Hello and goodbye

    Methods defined here:
        __init__()
            Wow, I have no function!

    Data descriptors defined here:
        __dict__
            dictionary for instance variables (if defined)
        __weakref__
            list of weak references to the object (if defined)

class B(builtins.object)
    Data descriptors defined here:
        __dict__
            dictionary for instance variables (if defined)
        __weakref__
            list of weak references to the object (if defined)
    Data and other attributes defined here:
        NO_MEANING = 'eggs'
        __annotations__ = {'NO_MEANING': <class 'str'>}


class C(builtins.object)
    Methods defined here:
        get_answer(self)
            Return say_no()
        is_it_true(self)
            Return self.get_answer()
        say_no(self)
    Data descriptors defined here:
        __dict__
            dictionary for instance variables (if defined)
        __weakref__
             list of weak references to the object (if defined)

Functions
    doc_func()
        This function solves all of the world's problems:
        hunger
        lack of Python
        war
    nodoc_func()

Data
    __xyz__ = 'X, Y and Z'

Author
    Benjamin Peterson

Credits
    Nobody
"""

expected_html_data_docstrings = tuple(
    s.replace(" ", "&nbsp;") for s in expected_data_docstrings
)

# output pattern for missing module
missing_pattern = """\
No Python documentation found for %r.
Use help() to get the interactive help utility.
Use help(str) for help on the str class.""".replace(
    "\n", os.linesep
)

# output pattern for module with bad imports
badimport_pattern = "problem in %s - ModuleNotFoundError: No module named %r"

expected_dynamicattribute_pattern = """
Help on class DA in module %s:

class DA(builtins.object)
 |  Data descriptors defined here:
 |\x20\x20
 |  __dict__%s
 |\x20\x20
 |  __weakref__%s
 |\x20\x20
 |  ham
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from Meta:
 |\x20\x20
 |  ham = 'spam'
""".strip()

expected_virtualattribute_pattern1 = """
Help on class Class in module %s:

class Class(builtins.object)
 |  Data and other attributes inherited from Meta:
 |\x20\x20
 |  LIFE = 42
""".strip()

expected_virtualattribute_pattern2 = """
Help on class Class1 in module %s:

class Class1(builtins.object)
 |  Data and other attributes inherited from Meta1:
 |\x20\x20
 |  one = 1
""".strip()

expected_virtualattribute_pattern3 = """
Help on class Class2 in module %s:

class Class2(Class1)
 |  Method resolution order:
 |      Class2
 |      Class1
 |      builtins.object
 |\x20\x20
 |  Data and other attributes inherited from Meta1:
 |\x20\x20
 |  one = 1
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from Meta3:
 |\x20\x20
 |  three = 3
 |\x20\x20
 |  ----------------------------------------------------------------------
 |  Data and other attributes inherited from Meta2:
 |\x20\x20
 |  two = 2
""".strip()

expected_missingattribute_pattern = """
Help on class C in module %s:

class C(builtins.object)
 |  Data and other attributes defined here:
 |\x20\x20
 |  here = 'present!'
""".strip()


def run_pydoc(module_name, *args, **env):
    """
    Runs pydoc on the specified module. Returns the stripped
    output of pydoc.
    """
    args = args + (module_name,)
    # do not write bytecode files to avoid caching errors
    rc, out, err = assert_python_ok("-B", pydoc.__file__, *args, **env)
    return out.strip()


def run_pydoc_fail(module_name, *args, **env):
    """
    Runs pydoc on the specified module expecting a failure.
    """
    args = args + (module_name,)
    rc, out, err = assert_python_failure("-B", pydoc.__file__, *args, **env)
    return out.strip()


def get_pydoc_html(module):
    "Returns pydoc generated output as html"
    doc = pydoc.HTMLDoc()
    output = doc.docmodule(module)
    loc = doc.getdocloc(pydoc_mod) or ""
    if loc:
        loc = '<br><a href="' + loc + '">Module Docs</a>'
    return output.strip(), loc


def get_html_title(text):
    # Bit of hack, but good enough for test purposes
    header, _, _ = text.partition("</head>")
    _, _, title = header.partition("<title>")
    title, _, _ = title.partition("</title>")
    return title


def html2text(html):
    """A quick and dirty implementation of html2text.

    Tailored for pydoc tests only.
    """
    return pydoc.replace(
        re.sub("<.*?>", "", html), "&nbsp;", " ", "&gt;", ">", "&lt;", "<"
    )


class PydocBaseTest(unittest.TestCase):
    def _restricted_walk_packages(self, walk_packages, path=None):
        """
        A version of pkgutil.walk_packages() that will restrict itself to
        a given path.
        """
        default_path = path or [os.path.dirname(__file__)]

        def wrapper(path=None, prefix="", onerror=None):
            return walk_packages(path or default_path, prefix, onerror)

        return wrapper

    @contextlib.contextmanager
    def restrict_walk_packages(self, path=None):
        walk_packages = pkgutil.walk_packages
        pkgutil.walk_packages = self._restricted_walk_packages(walk_packages, path)
        try:
            yield
        finally:
            pkgutil.walk_packages = walk_packages


class PydocDocTest(unittest.TestCase):
    maxDiff = None

    def test_stripid(self):
        # test with strings, other implementations might have different repr()
        stripid = pydoc.stripid
        # strip the id
        self.assertEqual(
            stripid("<function stripid at 0x88dcee4>"), "<function stripid>"
        )
        self.assertEqual(
            stripid("<function stripid at 0x01F65390>"), "<function stripid>"
        )
        # nothing to strip, return the same text
        self.assertEqual(stripid("42"), "42")
        self.assertEqual(
            stripid("<type 'exceptions.Exception'>"), "<type 'exceptions.Exception'>"
        )

    def test_synopsis(self):
        self.addCleanup(unlink, TESTFN)
        for encoding in ("ISO-8859-1", "UTF-8"):
            with open(TESTFN, "w", encoding=encoding) as script:
                if encoding != "UTF-8":
                    print("#coding: {}".format(encoding), file=script)
                print('"""line 1: h\xe9', file=script)
                print('line 2: hi"""', file=script)
            synopsis = pydoc.synopsis(TESTFN, {})
            self.assertEqual(synopsis, "line 1: h\xe9")

    def test_splitdoc_with_description(self):
        example_string = "I Am A Doc\n\n\nHere is my description"
        self.assertEqual(
            pydoc.splitdoc(example_string), ("I Am A Doc", "\nHere is my description")
        )

    def test_is_package_when_not_package(self):
        with os_helper.temp_cwd() as test_dir:
            self.assertFalse(pydoc.ispackage(test_dir))

    # def test_is_package_when_is_package(self):
    #     with os_helper.temp_cwd() as test_dir:
    #         init_path = os.path.join(test_dir, '__init__.py')
    #         print(init_path)
    #         open(init_path, 'w').close()
    #         self.assertTrue(pydoc.ispackage(test_dir))
    #         os.remove(init_path)


class TestDescriptions(unittest.TestCase):
    @requires_docstrings
    def test_html_for_https_links(self):
        def a_fn_with_https_link():
            """a link https://localhost/"""
            pass

        html = pydoc.HTMLDoc().document(a_fn_with_https_link)
        self.assertIn('<a href="https://localhost/">https://localhost/</a>', html)


def setUpModule():
    thread_info = threading_helper.threading_setup()
    unittest.addModuleCleanup(threading_helper.threading_cleanup, *thread_info)
    unittest.addModuleCleanup(reap_children)


if __name__ == "__main__":
    unittest.main()
