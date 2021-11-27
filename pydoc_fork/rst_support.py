"""
Rst to HTML function
Credits: https://stackoverflow.com/a/49047197/33264
"""
from docutils import core
from docutils.writers.html4css1 import HTMLTranslator, Writer


class HTMLFragmentTranslator(HTMLTranslator):
    def __init__(self, document):
        HTMLTranslator.__init__(self, document)
        self.head_prefix = ["", "", "", "", ""]
        self.body_prefix = []
        self.body_suffix = []
        self.stylesheet = []

    def astext(self):
        return "".join(self.body)


html_fragment_writer = Writer()
html_fragment_writer.translator_class = HTMLFragmentTranslator


def rst_to_html(text: str) -> str:
    return core.publish_string(text, writer=html_fragment_writer).decode("utf-8")
