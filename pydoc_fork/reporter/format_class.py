"""
Roughly a UI component for classes
"""
import builtins
import inspect
import sys
from collections import deque
from typing import Any, Callable, Dict, List, Optional, Union, cast

from pydoc_fork import settings
from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.utils import (
    _split_list,
    classify_class_attrs,
    classname,
    getdoc,
    sort_attributes,
    visiblename,
)
from pydoc_fork.reporter import inline_styles
from pydoc_fork.reporter.format_data import document_data
from pydoc_fork.reporter.format_other import docother
from pydoc_fork.reporter.formatter_html import markup, section


def classlink(the_object: Union[TypeLike, type], modname: str) -> str:
    """Make a link for a class."""
    name, module = the_object.__name__, sys.modules.get(the_object.__module__)
    if hasattr(module, name) and getattr(module, name) is the_object:
        return f'<a href="{module.__name__}.html#{name}">{classname(cast(TypeLike, the_object), modname)}</a>'
    return classname(the_object, modname)


# noinspection PyBroadException
def docclass(
    the_object: TypeLike,
    name: str = "",
    mod: str = "",
    funcs: Optional[Dict[str, str]] = None,
    classes: Optional[Dict[str, str]] = None,
) -> str:
    """Produce HTML documentation for a class object."""
    funcs = funcs or {}
    classes = classes or {}

    real_name = the_object.__name__
    name = name or real_name
    bases = the_object.__bases__

    contents: List[str] = []
    push = contents.append

    class HorizontalRule:
        """Cute little class to pump out a horizontal rule between sections."""

        def __init__(self) -> None:
            self.need_one = 0

        def maybe(self) -> None:
            """Skip"""
            if self.need_one:
                push("<hr>\n")
            self.need_one = 1

    # pylint:disable=invalid-name
    hr = HorizontalRule()

    # List the mro, if non-trivial.
    mro = deque(inspect.getmro(cast(type, the_object)))
    if len(mro) > 2:
        hr.maybe()
        push("<dl><dt>Method resolution order:</dt>\n")
        for base in mro:
            push(f"<dd>{classlink(base, the_object.__module__)}</dd>\n")
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
                # noinspection PyBroadException
                try:
                    value = getattr(the_object, name)
                except Exception:  # nosec
                    # Some descriptors may meet a failure in their __get__.
                    # (bug #1785)
                    push(
                        document_data(
                            value,
                            name,
                            # mod, unused
                        )
                    )
                else:
                    # circular ref
                    # pylint: disable=import-outside-toplevel
                    from pydoc_fork.reporter.format_page import document

                    push(
                        document(
                            value, name, mod, funcs, classes, module_dict, the_object
                        )
                    )
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
                    document_data(
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
                    push(f"<dl><dt>{base}</dl>\n")
                else:
                    found_doc = markup(getdoc(value), funcs, classes, module_dict)
                    found_doc = f"<dd><tt>{found_doc}</tt>"
                    push(f"<dl><dt>{base}{found_doc}</dl>\n")
                push("\n")
        return attrs

    attrs = [
        (name, kind, cls, value)
        for name, kind, cls, value in classify_class_attrs(the_object)
        if visiblename(name, obj=the_object)
    ]

    module_dict = {}
    for key, _, _, value in attrs:
        module_dict[key] = anchor = "#" + name + "-" + key
        try:
            value = getattr(the_object, name)
        except Exception:  # nosec
            # Some descriptors may meet a failure in their __get__.
            # (bug #1785)
            pass  # nosec
        try:
            # The value may not be hashable (e.g., a data attr with
            # a dict or list value).
            module_dict[value] = anchor
        except TypeError:
            pass  # nosec

    while attrs:
        if mro:
            this_class = mro.popleft()
        else:
            this_class = attrs[0][2]

        is_this_class: Callable[[Any], Any] = lambda t: t[2] is this_class
        attrs, inherited = _split_list(attrs, is_this_class)

        if the_object is not builtins.object and this_class is builtins.object:
            attrs = inherited
            continue
        if this_class is the_object:
            tag = "defined here"
        else:
            tag = f"inherited from {classlink(this_class, the_object.__module__)}"
        tag += ":<br>\n"

        sort_attributes(attrs, the_object)

        # feature to remove typing annotations cruft.
        for kind in attrs.copy():
            module_name = inspect.getmodule(kind)
            if module_name and module_name.__name__ in settings.SKIP_MODULES:
                attrs.remove(kind)

        # Pump out the attrs, segregated by kind.
        is_method: Callable[[Any], Any] = lambda t: t[1] == "method"
        attrs = spill(f"Methods {tag}", attrs, is_method)
        is_class: Callable[[Any], Any] = lambda t: t[1] == "class method"
        attrs = spill(f"Class methods {tag}", attrs, is_class)
        is_static: Callable[[Any], Any] = lambda t: t[1] == "static method"
        attrs = spill(f"Static methods {tag}", attrs, is_static)
        is_read_only: Callable[[Any], Any] = lambda t: t[1] == "readonly property"
        attrs = spilldescriptors(
            f"Readonly properties {tag}",
            attrs,
            is_read_only,
        )
        is_data_descriptor: Callable[[Any], Any] = lambda t: t[1] == "data descriptor"
        attrs = spilldescriptors(f"Data descriptors {tag}", attrs, is_data_descriptor)
        is_data: Callable[[Any], Any] = lambda t: t[1] == "data"
        attrs = spilldata(f"Data and other attributes {tag}", attrs, is_data)
        assert not attrs  # nosec
        attrs = inherited

    contents_as_string = "".join(contents)  # type got redefined

    if name == real_name:
        title = f'<a name="{name}">class <strong>{real_name}</strong></a>'
    else:
        title = f'<strong>{name}</strong> = <a name="{name}">class {real_name}</a>'
    if bases:
        parents = []
        for base in bases:
            parents.append(classlink(base, the_object.__module__))
        title = title + f"({', '.join(parents)})"

    decl = ""
    try:
        signature = inspect.signature(the_object)
    except (ValueError, TypeError):
        signature = None
    if signature:
        argument_specification = str(signature)
        if argument_specification and argument_specification != "()":
            # this will cause double escape on ->
            # escape(argument_specification)
            decl = name + argument_specification + "\n\n"

    doc = getdoc(the_object)
    if decl:
        doc = decl + (doc or "")
    doc = markup(doc, funcs, classes, module_dict)
    doc = doc and f"<tt>{doc}<br>&nbsp;</tt>"

    return section(title, "#000000", "#ffc8d8", contents_as_string, 3, doc)


def format_tree(tree: List[Any], modname: str, parent: Optional[Any] = None) -> str:
    """
    Creates a representation of class inheritance.

    Args:
        tree: list representing tree
        modname: module name
        parent: parent class

    Returns: html representing class hierarchy
    """

    # """Produce HTML for a class tree as given by inspect.getclasstree()."""
    result = ""
    for entry in tree:
        class_object = entry
        if type(entry) is type(()):  # noqa - not sure of switching to isinstance
            class_object, bases = entry
            result = (
                result + f'<dt><span style="font-family:{inline_styles.SAN_SERIF}">'
            )
            result = result + classlink(class_object, modname)
            if bases and bases != (parent,):
                parents = []
                for base in bases:
                    parents.append(classlink(base, modname))
                result = result + "(" + ", ".join(parents) + ")"
            result = result + "\n</span></dt>"
        elif type(entry) is type([]):  # noqa - not sure of switching to isinstance
            tree = format_tree(entry, modname, class_object)
            result = result + f"<dd>\n{tree}</dd>\n"
    return f"<dl>\n{result}</dl>\n"
