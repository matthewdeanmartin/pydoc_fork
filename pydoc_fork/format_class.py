"""
Roughly a UI component for classes
"""
import builtins
import inspect
import sys
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Union, cast

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.format_data import docdata
from pydoc_fork.format_other import docother
from pydoc_fork.formatter_html import escape, markup, section
from pydoc_fork.utils import (
    _split_list,
    classify_class_attrs,
    classname,
    getdoc,
    sort_attributes,
    visiblename,
)


def classlink(the_object: Union[TypeLike, type], modname: str) -> str:
    """Make a link for a class."""
    name, module = the_object.__name__, sys.modules.get(the_object.__module__)
    if hasattr(module, name) and getattr(module, name) is the_object:
        return '<a href="{}.html#{}">{}</a>'.format(
            module.__name__, name, classname(cast(TypeLike, the_object), modname)
        )
    return classname(the_object, modname)


def docclass(
    the_object: TypeLike,
    name: str = "",
    mod: str = "",
    funcs: Dict[str, str] = {},  # noqa - clean up later
    classes: Dict[str, str] = {},  # noqa - clean up later
    # *ignored: List[Any],
) -> str:
    """Produce HTML documentation for a class object."""
    realname = the_object.__name__
    name = name or realname
    bases = the_object.__bases__

    contents: List[str] = []
    push = contents.append

    class HorizontalRule:
        """Cute little class to pump out a horizontal rule between sections."""

        def __init__(self) -> None:
            self.needone = 0

        def maybe(self) -> None:
            if self.needone:
                push("<hr>\n")
            self.needone = 1

    hr = HorizontalRule()

    # List the mro, if non-trivial.
    mro = deque(inspect.getmro(cast(type, the_object)))
    if len(mro) > 2:
        hr.maybe()
        push("<dl><dt>Method resolution order:</dt>\n")
        for base in mro:
            push("<dd>%s</dd>\n" % classlink(base, the_object.__module__))
        push("</dl>\n")

    def spill(
        msg: str, attrs_in: List[Any], predicate: Callable[[Any], Any]
    ) -> List[Any]:
        """Not sure"""
        ok, attrs = _split_list(attrs_in, predicate)
        if ok:
            hr.maybe()
            push(msg)
            for name, _, _, value in ok:
                try:
                    value = getattr(the_object, name)
                except Exception:  # nosec
                    # Some descriptors may meet a failure in their __get__.
                    # (bug #1785)
                    push(
                        docdata(
                            value,
                            name,
                            # mod, unused
                        )
                    )
                else:
                    # circular ref
                    from pydoc_fork.format_page import document

                    push(document(value, name, mod, funcs, classes, mdict, the_object))
                push("\n")
        return attrs

    def spilldescriptors(
        msg: str,
        attrs_in: List[Any],  # Tuple[str, str, type, "object"]
        predicate: Callable[[Any], bool],
    ) -> List[Any]:
        """Not sure"""
        ok, attrs = _split_list(attrs_in, predicate)
        if ok:
            hr.maybe()
            push(msg)
            for name, _, _, value in ok:
                push(
                    docdata(
                        value,
                        name,
                        # mod, ignored
                    )
                )
        return attrs

    def spilldata(
        msg: str, attrs_in: List[Any], predicate: Callable[[Any], bool]
    ) -> List[Any]:
        """Not sure"""
        ok, attrs = _split_list(attrs_in, predicate)
        if ok:
            hr.maybe()
            push(msg)
            for name, _, __, value in ok:
                base = docother(
                    getattr(the_object, name),
                    name,
                    # mod ignored
                )
                found_doc = getdoc(value)
                if not found_doc:
                    push("<dl><dt>%s</dl>\n" % base)
                else:
                    found_doc = markup(getdoc(value), funcs, classes, mdict)
                    found_doc = "<dd><tt>%s</tt>" % found_doc
                    push(f"<dl><dt>{base}{found_doc}</dl>\n")
                push("\n")
        return attrs

    attrs = [
        (name, kind, cls, value)
        for name, kind, cls, value in classify_class_attrs(the_object)
        if visiblename(name, obj=the_object)
    ]

    mdict = {}
    for key, _, _, value in attrs:
        mdict[key] = anchor = "#" + name + "-" + key
        try:
            value = getattr(the_object, name)
        except Exception:  # nosec
            # Some descriptors may meet a failure in their __get__.
            # (bug #1785)
            pass  # nosec
        try:
            # The value may not be hashable (e.g., a data attr with
            # a dict or list value).
            mdict[value] = anchor
        except TypeError:
            pass  # nosec

    while attrs:
        if mro:
            thisclass = mro.popleft()
        else:
            thisclass = attrs[0][2]

        is_thisclass: Callable[[Any], Any] = lambda t: t[2] is thisclass
        attrs, inherited = _split_list(attrs, is_thisclass)

        if the_object is not builtins.object and thisclass is builtins.object:
            attrs = inherited
            continue
        elif thisclass is the_object:
            tag = "defined here"
        else:
            tag = "inherited from %s" % classlink(thisclass, the_object.__module__)
        tag += ":<br>\n"

        sort_attributes(attrs, the_object)

        # Pump out the attrs, segregated by kind.
        is_method: Callable[[Any], Any] = lambda t: t[1] == "method"
        attrs = spill("Methods %s" % tag, attrs, is_method)
        is_class: Callable[[Any], Any] = lambda t: t[1] == "class method"
        attrs = spill("Class methods %s" % tag, attrs, is_class)
        is_static: Callable[[Any], Any] = lambda t: t[1] == "static method"
        attrs = spill("Static methods %s" % tag, attrs, is_static)
        is_read_only: Callable[[Any], Any] = lambda t: t[1] == "readonly property"
        attrs = spilldescriptors(
            "Readonly properties %s" % tag,
            attrs,
            is_read_only,
        )
        is_data_descriptor: Callable[[Any], Any] = lambda t: t[1] == "data descriptor"
        attrs = spilldescriptors("Data descriptors %s" % tag, attrs, is_data_descriptor)
        is_data: Callable[[Any], Any] = lambda t: t[1] == "data"
        attrs = spilldata("Data and other attributes %s" % tag, attrs, is_data)
        assert attrs == []  # nosec
        attrs = inherited

    contents_as_string = "".join(contents)  # type got redefined

    if name == realname:
        title = f'<a name="{name}">class <strong>{realname}</strong></a>'
    else:
        title = '<strong>{}</strong> = <a name="{}">class {}</a>'.format(
            name, name, realname
        )
    if bases:
        parents = []
        for base in bases:
            parents.append(classlink(base, the_object.__module__))
        title = title + "(%s)" % ", ".join(parents)

    decl = ""
    try:
        signature = inspect.signature(the_object)
    except (ValueError, TypeError):
        signature = None
    if signature:
        argspec = str(signature)
        if argspec and argspec != "()":
            decl = name + escape(argspec) + "\n\n"

    doc = getdoc(the_object)
    if decl:
        doc = decl + (doc or "")
    doc = markup(doc, funcs, classes, mdict)
    doc = doc and "<tt>%s<br>&nbsp;</tt>" % doc

    return section(title, "#000000", "#ffc8d8", contents_as_string, 3, doc)


def formattree(tree: List[Any], modname: str, parent: Optional[Any] = None) -> str:
    """Produce HTML for a class tree as given by inspect.getclasstree()."""
    result = ""
    for entry in tree:
        if type(entry) is type(()):  # noqa - not sure of switching to isinstance
            class_object, bases = entry
            result = result + '<dt><font face="helvetica, arial">'
            result = result + classlink(class_object, modname)
            if bases and bases != (parent,):
                parents = []
                for base in bases:
                    parents.append(classlink(base, modname))
                result = result + "(" + ", ".join(parents) + ")"
            result = result + "\n</font></dt>"
        elif type(entry) is type([]):  # noqa - not sure of switching to isinstance
            result = result + "<dd>\n%s</dd>\n" % formattree(
                entry, modname, class_object
            )
    return "<dl>\n%s</dl>\n" % result
