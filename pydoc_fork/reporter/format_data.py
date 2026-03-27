"""
Roughly a UI component for variables and their values
"""

from typing import List

from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.utils import getdoc
from pydoc_fork.reporter.formatter_html import markup


def document_data(
    the_object: TypeLike,
    name: str = "",
) -> str:
    """Produce html documentation for a data descriptor."""
    from pydoc_fork.reporter.jinja_code import JINJA_ENV
    template = JINJA_ENV.get_template("data.jinja2")
    doc = markup(getdoc(the_object))
    return template.render(name=name, doc=doc)
