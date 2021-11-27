import http.server
from datetime import datetime

import html5lib
import sys

from pydoc_fork import describe
from pydoc_fork.format_other import docother
from pydoc_fork.utils import isdata, _find_doc_string


class Thing:
    blah = 1

    def __init__(self):
        self.self_thing = 123


def test_describe():
    various_types = [
        http.server.HTTPServer,
        http.server.SimpleHTTPRequestHandler,
        str,
        int,
        datetime,
        datetime.time,
        datetime.day,
        html5lib,
        docother,
        list,
        dict,
        [],
        {},
        set,
        set(),
        len,
        Thing,
        Thing.blah,
        Thing().self_thing,
        sys,
    ]

    for thing in various_types:
        assert describe(thing)


# def test_splitdoc():
#     # splits 1st line, blank, rest
#     synopsis, remainder = splitdoc("""
#     synopsis
#
#     Not synopsis.
#     """)
#     # trims this
#     assert synopsis == "synopsis"
#     # Doesn't trim!
#     assert remainder == "    Not synopsis."
#
#     synopsis, remainder = splitdoc("""
#         synopsis
#         Not synopsis.
#         """)
#     # Nothing is default text!
#     assert synopsis == ""
#     # Now this holds everything. Not HTML
#     assert remainder == 'synopsis\n        Not synopsis.'


def test_isdata():
    various_types = [
        http.server.HTTPServer,
        http.server.SimpleHTTPRequestHandler,
        str,
        int,
        datetime,
        datetime.time,
        # datetime.day,
        html5lib,
        docother,
        list,
        dict,
        set,
        len,
        Thing,
        sys,
    ]
    for thing in various_types:
        assert not isdata(thing)
    various_types = [
        datetime.day,
        [],
        {},
        set(),
        Thing.blah,
        Thing().self_thing,
    ]
    for thing in various_types:
        assert isdata(thing)


def test_finddoc():
    various_without = [
        http.server.HTTPServer,
        http.server.SimpleHTTPRequestHandler,
        str,
        int,
        list,
        dict,
        set,
        len,
        Thing,
        datetime,
        html5lib,
        docother,
        sys,
        datetime.day,
    ]
    various_types = [
        datetime.time,
    ]
    for thing in various_types:
        assert _find_doc_string(thing)
    for thing in various_without:
        assert _find_doc_string(thing) in [None, ""]
