"""
Roughly a UI component for data
"""
from typing import List

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.formatter_html import markup
from pydoc_fork.utils import getdoc


def docdata(
    the_object: TypeLike,
    name: str = "",  # Null safety
    # mod: Optional[str] = None,
    # cl: Optional[str] = None,
) -> str:
    """Produce html documentation for a data descriptor."""
    results: List[str] = []
    push = results.append

    if name:
        push("<dl><dt><strong>%s</strong></dt>\n" % name)
    doc = markup(getdoc(the_object))
    if doc:
        push("<dd><tt>%s</tt></dd>\n" % doc)
    push("</dl>\n")

    return "".join(results)
