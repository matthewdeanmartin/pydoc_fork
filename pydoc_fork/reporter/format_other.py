"""
Fallback docs
"""
from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.reporter.formatter_html import html_repr


def docother(
    the_object: TypeLike,
    name: str = "",
) -> str:
    """Produce HTML documentation for a data object."""
    lhs = name and f"<strong>{name}</strong> = " or ""
    return lhs + html_repr(the_object)
