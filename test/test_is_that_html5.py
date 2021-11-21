import http.server
from datetime import datetime

import html5lib

from pydoc_fork.format_class import docclass
from pydoc_fork.format_other import docother
from pydoc_fork.format_routine import docroutine
from pydoc_fork.formatter_html import section, bigsection, preformat, markup

HTML5PARSER = html5lib.HTMLParser(strict=True)

VARIOUS_TYPES = [str, int, datetime, datetime.time, datetime.day, html5lib, docother]


def test_docother():
    for thing in VARIOUS_TYPES:
        result = docother(thing, "various")
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_docroutine():
    various_methods = [datetime.time, test_docother, lambda x: 5]
    for thing in various_methods:
        result = docroutine(thing, "methods")
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_docclass():
    various_classes = [http.server.HTTPServer, http.server.SimpleHTTPRequestHandler]
    for thing in various_classes:
        result = docclass(thing, "methods")
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_section():
    # section(title, "#000000", "#ffc8d8", contents_as_string, 3, doc)
    for i in range(0, 6):
        print(f"-------{i}--------")
        result = section(
            "the title", "#000000", "#ffc8d8", "the contents", i, "the prelude"
        )
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_bigsection():
    # this just calls section & wrps results in a tag
    for i in range(0, 6):
        print(f"-------{i}--------")
        result = bigsection(
            "the title", "#000000", "#ffc8d8", "the contents", i, "the prelude"
        )
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_preformat():
    whitespace_things = ["cat\n\ndog", "cat\n \ndog", "cat \n \n dog"]
    for thing in whitespace_things:
        print("-------")
        result = preformat(thing)
        print(result)
        html = HTML5PARSER.parseFragment(result)


def test_markup():
    # this is some text to html converter
    various_text = [
        "RFC-123",
        "PEP-123",
        "https://google.com",
        "self.method(results:str)",
    ]
    for text in various_text:
        print("\n--------")
        result = markup(
            text=text, funcs={}, classes={}, methods={"method": "blah blah blah"}
        )
        print(result)
        html = HTML5PARSER.parseFragment(result)
