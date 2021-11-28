"""
Unclassified utils
"""
import inspect
import logging
import re
import sys
from modulefinder import Module
from typing import Any, Callable, List, Optional, Sequence, Tuple, Union, cast

from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.module_utils import locate

LOGGER = logging.getLogger(__name__)


def resolve(thing: Union[str, Any], force_load: bool = False) -> Tuple[Any, Any]:
    """Given an object or a path to an object, get the object and its name."""
    if isinstance(thing, str):
        the_object = locate(thing, force_load)
        if the_object is None:

            raise ImportError(
                """\
No Python documentation found for %r."""
                % thing
            )
        return the_object, thing

    name = getattr(thing, "__name__", None)
    if isinstance(name, str):
        return thing, name
    return thing, str(thing)  # HACK


def describe(thing: TypeLike) -> str:
    """Produce a short description of the given thing."""
    if inspect.ismodule(thing):
        if thing.__name__ in sys.builtin_module_names:
            return "built-in module " + thing.__name__
        if hasattr(thing, "__path__"):
            return "package " + thing.__name__
        return "module " + thing.__name__
    if inspect.isbuiltin(thing):
        return "built-in function " + thing.__name__
    if inspect.isgetsetdescriptor(thing):
        return f"getset descriptor {thing.__objclass__.__module__}.{thing.__objclass__.__name__}.{thing.__name__}"
    if inspect.ismemberdescriptor(thing):
        return f"member descriptor {thing.__objclass__.__module__}.{thing.__objclass__.__name__}.{thing.__name__}"
    if inspect.isclass(thing):
        return "class " + thing.__name__
    if inspect.isfunction(thing):
        return "function " + thing.__name__
    if inspect.ismethod(thing):
        return "method " + thing.__name__
    return type(thing).__name__


def _find_class(func: TypeLike) -> Optional[Module]:
    """Find a Class"""
    cls = sys.modules.get(func.__module__)
    if cls is None:
        return None
    for name in func.__qualname__.split(".")[:-1]:
        cls = getattr(cls, name)
    if not inspect.isclass(cls):
        return None
    return cls  # type: ignore


def _find_doc_string(obj: TypeLike) -> Optional[str]:
    """Find doc string"""
    if inspect.ismethod(obj):
        name = obj.__func__.__name__
        self = obj.__self__
        if (
            inspect.isclass(self)
            and getattr(getattr(self, name, None), "__func__") is obj.__func__  # noqa
        ):
            # class_method
            cls = self
        else:
            cls = self.__class__
    elif inspect.isfunction(obj):
        name = obj.__name__
        cls = _find_class(obj)
        if cls is None or getattr(cls, name) is not obj:
            return None
    elif inspect.isbuiltin(obj):
        name = obj.__name__
        self = obj.__self__
        if inspect.isclass(self) and self.__qualname__ + "." + name == obj.__qualname__:
            # class_method
            cls = self
        else:
            cls = self.__class__
    # Should be tested before isdatadescriptor().
    elif isinstance(obj, property):
        func = obj.fget
        name = func.__name__
        cls = _find_class(cast(TypeLike, func))
        if cls is None or getattr(cls, name) is not obj:
            return None
    elif inspect.ismethoddescriptor(obj) or inspect.isdatadescriptor(obj):
        name = obj.__name__
        cls = obj.__objclass__
        if getattr(cls, name) is not obj:
            return None
        if inspect.ismemberdescriptor(obj):
            slots = getattr(cls, "__slots__", None)
            if isinstance(slots, dict) and name in slots:
                return slots[name]
    else:
        return None
    for base in cls.__mro__:
        try:
            doc = _get_own_doc_string(getattr(base, name))
        except AttributeError:
            continue
        if doc is not None:
            return doc
    return None


def _get_own_doc_string(obj: TypeLike) -> str:
    """Get the documentation string for an object if it is not
    inherited from its class."""
    try:
        doc = object.__getattribute__(obj, "__doc__")
        if doc is None:
            return ""  # null safety
        if obj is not type:
            typedoc = type(obj).__doc__
            if isinstance(typedoc, str) and typedoc == doc:
                return ""  # null safety
        return cast(str, doc)
    except AttributeError:
        LOGGER.debug(f"No docstring for {str(obj)}")
        return ""  # null safety


def _getdoc(the_object: TypeLike) -> str:
    """
    Get the documentation string for an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up with blocks of code, any whitespace than can be
    uniformly removed from the second line onwards is removed.
    """
    doc = _get_own_doc_string(the_object)
    if doc is None:
        try:
            doc = _find_doc_string(the_object)
        except (AttributeError, TypeError):
            return ""  # null safety
    if not isinstance(doc, str):
        return ""  # null safety
    return inspect.cleandoc(doc)


def getdoc(the_object: TypeLike) -> str:
    """Get the doc string or comments for an object."""
    result = _getdoc(the_object) or inspect.getcomments(the_object)
    return result and re.sub("^ *\n", "", result.rstrip()) or ""


def classname(the_object: TypeLike, modname: str) -> str:
    """Get a class name and qualify it with a module name if necessary."""
    name = the_object.__name__
    if the_object.__module__ != modname:
        name = the_object.__module__ + "." + name
    return name


def isdata(the_object: Any) -> bool:
    """Check if an object is of a type that probably means it's data."""
    return not (
        inspect.ismodule(the_object)
        or inspect.isclass(the_object)
        or inspect.isroutine(the_object)
        or inspect.isframe(the_object)
        or inspect.istraceback(the_object)
        or inspect.iscode(the_object)
    )


def _is_bound_method(the_function: object) -> bool:
    """
    Returns True if fn is a bound method, regardless of whether
    fn was implemented in Python or in C.
    """
    if inspect.ismethod(the_function):
        return True
    if inspect.isbuiltin(the_function):
        self = getattr(the_function, "__self__", None)
        return not (inspect.ismodule(self) or (self is None))
    return False


# def all_methods(cl: type) -> Dict[str, Any]:
#     """all methods"""
#     methods = {}
#     for key, value in inspect.getmembers(cl, inspect.isroutine):
#         methods[key] = 1
#     for base in cl.__bases__:
#         methods.update(all_methods(base))  # all your base are belong to us
#     for key in methods.keys():
#         methods[key] = getattr(cl, key)
#     return methods


def _split_list(
    the_sequence: Sequence[Any], predicate: Callable[[Any], Any]
) -> Tuple[List[Any], List[Any]]:
    """Split sequence s via predicate, and return pair ([true], [false]).

    The return value is a 2-tuple of lists,
        ([x for x in s if predicate(x)],
         [x for x in s if not predicate(x)])
    """

    yes = []
    # pylint: disable=invalid-name
    no = []
    for x in the_sequence:
        if predicate(x):
            yes.append(x)
        else:
            no.append(x)
    return yes, no


def visiblename(
    name: str, all_things: Optional[List[str]] = None, obj: Optional[Any] = None
) -> bool:
    """Decide whether to show documentation on a variable."""
    # Certain special names are redundant or internal.
    # XXX Remove __initializing__?
    if name in {
        "__author__",
        "__builtins__",
        "__cached__",
        "__credits__",
        "__date__",
        "__doc__",
        "__file__",
        "__spec__",
        "__loader__",
        "__module__",
        "__name__",
        "__package__",
        "__path__",
        "__qualname__",
        "__slots__",
        "__version__",
    }:
        return False
    # Private names are hidden, but special names are displayed.
    if name.startswith("__") and name.endswith("__"):
        return True
    # Namedtuples have public fields and methods with a single leading underscore
    if name.startswith("_") and hasattr(obj, "_fields"):
        return True
    if all_things is not None:
        # only document that which the programmer exported in __all__
        return name in all_things
    return not name.startswith("_")


def classify_class_attrs(the_object: TypeLike) -> List[Tuple[str, str, type, object]]:
    """Wrap inspect.classify_class_attrs, with fixup for data descriptors."""
    results = []
    try:
        for (name, kind, cls, value) in inspect.classify_class_attrs(
            cast(type, the_object)
        ):
            if inspect.isdatadescriptor(value):
                kind = "data descriptor"
                if isinstance(value, property) and value.fset is None:
                    kind = "readonly property"
            results.append((name, kind, cls, value))
    except ValueError:
        LOGGER.warning(f"Skipping classify_class_attrs for {str(the_object)} got ValueError, maybe this is a Namespace")
        # py._xmlgen.Namespace
        # ValueError: Namespace class is abstract
        pass
    return results


def sort_attributes(attrs: List[Any], the_object: Union[TypeLike, type]) -> None:
    """Sort the attrs list in-place by _fields and then alphabetically by name"""
    # This allows data descriptors to be ordered according
    # to a _fields attribute if present.
    fields = getattr(the_object, "_fields", [])
    try:
        field_order = {name: i - len(fields) for (i, name) in enumerate(fields)}
    except TypeError:
        field_order = {}

    def key_function(attr: List[Any]) -> Tuple[Any, Any]:
        """Sorting function"""
        return field_order.get(attr[0], 0), attr[0]

    attrs.sort(key=key_function)
