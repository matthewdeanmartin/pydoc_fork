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
    from pydoc_fork.reporter.jinja_code import JINJA_ENV

    template = JINJA_ENV.get_template("fallback.jinja2")
    return template.render(name=name, value_repr=html_repr(the_object))
