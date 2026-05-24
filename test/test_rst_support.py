import pytest
from docutils import core

from pydoc_fork.reporter import rst_support


def test_rst_to_html_returns_html_fragment():
    result = rst_support.rst_to_html("Heading\n=======\n\nParagraph with **bold** text.")

    assert result.startswith("<!DOCTYPE html")
    assert "<h1" in result
    assert "<strong>bold</strong>" in result
    assert '<div class="document"' in result


def test_html_fragment_translator_methods():
    document = core.publish_doctree("hello")
    defaults = {
        "initial_header_level": 1,
        "math_output": "MathJax",
        "stylesheet": "",
        "stylesheet_path": None,
        "xml_declaration": False,
        "output_encoding": "unicode",
        "embed_stylesheet": False,
        "cloak_email_addresses": False,
        "compact_lists": False,
        "compact_field_lists": False,
        "table_style": "",
        "field_name_limit": 14,
        "option_limit": 14,
        "footnote_references": "brackets",
        "attribution": "dash",
    }
    for name, value in defaults.items():
        setattr(document.settings, name, value)
    translator = rst_support.HTMLFragmentTranslator(document)
    translator.body.extend(["<p>", "hello", "</p>"])

    assert translator.astext() == "<p>hello</p>"

    with pytest.raises(NotImplementedError, match="FakeNode"):
        translator.unimplemented_visit(type("FakeNode", (), {})())
