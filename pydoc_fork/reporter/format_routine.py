"""
Roughly a UI component for routines
"""
import inspect
from typing import Any, Dict, Optional

from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.utils import _is_bound_method, getdoc
from pydoc_fork.reporter import inline_styles
from pydoc_fork.reporter.format_class import classlink
from pydoc_fork.reporter.formatter_html import disabled_text, escape, markup


def docroutine(
    the_object: TypeLike,
    name: str = "",
    mod: str = "",
    funcs: Optional[Dict[str, Any]] = None,  # noqa - clean up later
    classes: Optional[Dict[str, Any]] = None,  # noqa - clean up later
    methods: Optional[Dict[str, Any]] = None,  # noqa - clean up later
    cl: Optional[TypeLike] = None,
) -> str:
    """Produce HTML documentation for a function or method object."""
    if not funcs:
        funcs = {}
    if not classes:
        classes = {}
    if not methods:
        methods = {}
    # AttributeError: 'cached_property' object has no attribute '__name__'
    try:
        real_name = the_object.__name__
    except AttributeError:
        real_name = None
    name = name or real_name
    anchor = (cl and cl.__name__ or "") + "-" + name
    note = ""
    skip_docs = 0
    if _is_bound_method(the_object):
        imported_class = the_object.__self__.__class__
        if cl:
            if imported_class is not cl:
                note = " from " + classlink(imported_class, mod)
        else:
            if the_object.__self__ is not None:
                link = classlink(the_object.__self__.__class__, mod)
                note = f" method of {link} instance"
            else:
                link = classlink(imported_class, mod)
                note = f" unbound {link} method"

    if inspect.iscoroutinefunction(the_object) or inspect.isasyncgenfunction(
        the_object
    ):
        async_qualifier = "async "
    else:
        async_qualifier = ""

    if name == real_name:
        title = f'<a name="{anchor}"><strong>{real_name}</strong></a>'
    else:
        if cl and inspect.getattr_static(cl, real_name, []) is the_object:
            real_link = f'<a href="#{cl.__name__ + "-" + real_name}">{real_name}</a>'
            skip_docs = 1
        else:
            real_link = real_name
        title = f'<a name="{anchor}"><strong>{name}</strong></a> = {real_link}'
    argument_specification = None
    if inspect.isroutine(the_object):
        try:
            signature: Optional[inspect.Signature] = inspect.signature(the_object)
        except (ValueError, TypeError):
            signature = None
        if signature:
            argument_specification = str(signature)
            if real_name == "<lambda>":
                title = f"<strong>{name}</strong> <em>lambda</em> "
                # XXX lambda's won't usually have func_annotations['return']
                # since the syntax doesn't support but it is possible.
                # So removing parentheses isn't truly safe.
                argument_specification = argument_specification[
                    1:-1
                ]  # remove parentheses
    if not argument_specification:
        argument_specification = "(...)"

    decl = (
        async_qualifier
        + title
        + escape(argument_specification)
        + (
            note
            and disabled_text(
                f'<span style="font-family:{inline_styles.SAN_SERIF}">{note}</span>'
            )
        )
    )

    if skip_docs:
        return f"<dl><dt>{decl}</dt></dl>\n"

    doc = markup(getdoc(the_object), funcs, classes, methods)
    doc = doc and f"<dd><tt>{doc}</tt></dd>"
    return f"<dl><dt>{decl}</dt>{doc}</dl>\n"
