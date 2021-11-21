"""
Fallback docs
"""
from pydoc_fork.custom_types import TypeLike
from pydoc_fork.formatter_html import html_repr


def docother(
    the_object: TypeLike,
    name: str = "",  # Null safety,
) -> str:
    """Produce HTML documentation for a data object."""
    lhs = name and "<strong>%s</strong> = " % name or ""
    return lhs + html_repr(the_object)
