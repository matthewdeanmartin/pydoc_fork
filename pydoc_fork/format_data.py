"""
Roughly a UI component for variables and their values
"""
from typing import List

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.formatter_html import markup
from pydoc_fork.utils import getdoc


def document_data(
    the_object: TypeLike,
    name: str = "",
) -> str:
    """Produce html documentation for a data descriptor."""

    results: List[str] = []

    if name:
        results.append(f"<dl><dt><strong>{name}</strong></dt>\n")
    doc = markup(getdoc(the_object))
    if doc:
        results.append(f"<dd><tt>{doc}</tt></dd>\n")
    results.append("</dl>\n")

    return "".join(results)
