"""
Rst to HTML function
Credits: https://stackoverflow.com/a/49047197/33264
"""

from typing import Any

from docutils import core
from docutils.writers.html4css1 import HTMLTranslator, Writer


class HTMLFragmentTranslator(HTMLTranslator):
    """Minimum to call docutils"""

    def __init__(self, document: Any) -> None:
        """setup"""
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ["", "", "", "", ""]
        self.body_prefix: list[Any] = []
        self.body_suffix: list[Any] = []
        self.stylesheet: list[Any] = []

    def astext(self) -> str:
        """minimum to call docutils"""
        return "".join(self.body)


html_fragment_writer = Writer()
html_fragment_writer.translator_class = HTMLFragmentTranslator


def rst_to_html(text: str) -> str:
    """Convert rst string to html string"""
    return core.publish_string(text, writer=html_fragment_writer).decode("utf-8")
