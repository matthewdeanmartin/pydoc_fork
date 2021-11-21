"""
Roughly a UI component for routines
"""
import inspect
from typing import Any, Dict, Optional

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.format_class import classlink
from pydoc_fork.formatter_html import escape, grey, markup
from pydoc_fork.utils import _is_bound_method, getdoc


def docroutine(
    the_object: TypeLike,
    name: str = "",
    mod: str = "",
    funcs: Dict[str, Any] = {},  # noqa - clean up later
    classes: Dict[str, Any] = {},  # noqa - clean up later
    methods: Dict[str, Any] = {},  # noqa - clean up later
    cl: Optional[TypeLike] = None,
) -> str:
    """Produce HTML documentation for a function or method object."""
    realname = the_object.__name__
    name = name or realname
    anchor = (cl and cl.__name__ or "") + "-" + name
    note = ""
    skipdocs = 0
    if _is_bound_method(the_object):
        imclass = the_object.__self__.__class__
        if cl:
            if imclass is not cl:
                note = " from " + classlink(imclass, mod)
        else:
            if the_object.__self__ is not None:
                link = classlink(the_object.__self__.__class__, mod)
                note = f" method of {link} instance"
            else:
                link = classlink(imclass, mod)
                note = f" unbound {link} method"

    if inspect.iscoroutinefunction(the_object) or inspect.isasyncgenfunction(
        the_object
    ):
        asyncqualifier = "async "
    else:
        asyncqualifier = ""

    if name == realname:
        title = f'<a name="{anchor}"><strong>{realname}</strong></a>'
    else:
        if cl and inspect.getattr_static(cl, realname, []) is the_object:
            reallink = f'<a href="#{cl.__name__ + "-" + realname}">{realname}</a>'
            skipdocs = 1
        else:
            reallink = realname
        title = f'<a name="{anchor}"><strong>{name}</strong></a> = {reallink}'
    argspec = None
    if inspect.isroutine(the_object):
        try:
            signature = inspect.signature(the_object)
        except (ValueError, TypeError):
            signature = None
        if signature:
            argspec = str(signature)
            if realname == "<lambda>":
                title = f"<strong>{name}</strong> <em>lambda</em> "
                # XXX lambda's won't usually have func_annotations['return']
                # since the syntax doesn't support but it is possible.
                # So removing parentheses isn't truly safe.
                argspec = argspec[1:-1]  # remove parentheses
    if not argspec:
        argspec = "(...)"

    decl = (
        asyncqualifier
        + title
        + escape(argspec)
        + (note and grey(f'<font face="helvetica, arial">{note}</font>'))
    )

    if skipdocs:
        return f"<dl><dt>{decl}</dt></dl>\n"

    doc = markup(getdoc(the_object), funcs, classes, methods)
    doc = doc and f"<dd><tt>{doc}</tt></dd>"
    return f"<dl><dt>{decl}</dt>{doc}</dl>\n"
