import importlib._bootstrap
import importlib._bootstrap_external
import importlib.machinery
import importlib.util
import inspect
import os
import re
import sys
import tokenize
from typing import Any, Callable, Dict, Optional, Sequence, TextIO, Tuple, Union

from pydoc_fork.custom_types import ModuleLike, TypeLike
from pydoc_fork.module_utils import locate


def resolve(thing: Union[str, Any], forceload: int = 0) -> Tuple[Any, Any]:
    """Given an object or a path to an object, get the object and its name."""
    if isinstance(thing, str):
        object = locate(thing, forceload)
        if object is None:
            raise ImportError(
                """\
No Python documentation found for %r.
Use help() to get the interactive help utility.
Use help(str) for help on the str class."""
                % thing
            )
        return object, thing
    else:
        name = getattr(thing, "__name__", None)
        return thing, name if isinstance(name, str) else None


def describe(thing: TypeLike) -> str:
    """Produce a short description of the given thing."""
    if inspect.ismodule(thing):
        if thing.__name__ in sys.builtin_module_names:
            return "built-in module " + thing.__name__
        if hasattr(thing, "__path__"):
            return "package " + thing.__name__
        else:
            return "module " + thing.__name__
    if inspect.isbuiltin(thing):
        return "built-in function " + thing.__name__
    if inspect.isgetsetdescriptor(thing):
        return "getset descriptor {}.{}.{}".format(
            thing.__objclass__.__module__, thing.__objclass__.__name__, thing.__name__
        )
    if inspect.ismemberdescriptor(thing):
        return "member descriptor {}.{}.{}".format(
            thing.__objclass__.__module__, thing.__objclass__.__name__, thing.__name__
        )
    if inspect.isclass(thing):
        return "class " + thing.__name__
    if inspect.isfunction(thing):
        return "function " + thing.__name__
    if inspect.ismethod(thing):
        return "method " + thing.__name__
    return type(thing).__name__


def _findclass(func: ModuleLike) -> Optional[str]:
    cls = sys.modules.get(func.__module__)
    if cls is None:
        return None
    for name in func.__qualname__.split(".")[:-1]:
        cls = getattr(cls, name)
    if not inspect.isclass(cls):
        return None
    return cls


def _finddoc(obj: Any) -> Optional[str]:
    if inspect.ismethod(obj):
        name = obj.__func__.__name__
        self = obj.__self__
        if (
            inspect.isclass(self)
            and getattr(getattr(self, name, None), "__func__") is obj.__func__
        ):
            # classmethod
            cls = self
        else:
            cls = self.__class__
    elif inspect.isfunction(obj):
        name = obj.__name__
        cls = _findclass(obj)
        if cls is None or getattr(cls, name) is not obj:
            return None
    elif inspect.isbuiltin(obj):
        name = obj.__name__
        self = obj.__self__
        if inspect.isclass(self) and self.__qualname__ + "." + name == obj.__qualname__:
            # classmethod
            cls = self
        else:
            cls = self.__class__
    # Should be tested before isdatadescriptor().
    elif isinstance(obj, property):
        func = obj.fget
        name = func.__name__
        cls = _findclass(func)
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
            doc = _getowndoc(getattr(base, name))
        except AttributeError:
            continue
        if doc is not None:
            return doc
    return None


def _getowndoc(obj: Any) -> Optional[str]:
    """Get the documentation string for an object if it is not
    inherited from its class."""
    try:
        doc = object.__getattribute__(obj, "__doc__")
        if doc is None:
            return None
        if obj is not type:
            typedoc = type(obj).__doc__
            if isinstance(typedoc, str) and typedoc == doc:
                return None
        return doc
    except AttributeError:
        return None


def _getdoc(object: TypeLike) -> Optional[str]:
    """Get the documentation string for an object.

    All tabs are expanded to spaces.  To clean up docstrings that are
    indented to line up with blocks of code, any whitespace than can be
    uniformly removed from the second line onwards is removed."""
    doc = _getowndoc(object)
    if doc is None:
        try:
            doc = _finddoc(object)
        except (AttributeError, TypeError):
            return None
    if not isinstance(doc, str):
        return None
    return inspect.cleandoc(doc)


def getdoc(object: TypeLike) -> Optional[str]:
    """Get the doc string or comments for an object."""
    result = _getdoc(object) or inspect.getcomments(object)
    return result and re.sub("^ *\n", "", result.rstrip()) or ""


def splitdoc(doc: str) -> Tuple[str, str]:
    """Split a doc string into a synopsis line (if any) and the rest."""
    lines = doc.strip().split("\n")
    if len(lines) == 1:
        return lines[0], ""
    elif len(lines) >= 2 and not lines[1].rstrip():
        return lines[0], "\n".join(lines[2:])
    return "", "\n".join(lines)


def classname(object: TypeLike, modname: str) -> str:
    """Get a class name and qualify it with a module name if necessary."""
    name = object.__name__
    if object.__module__ != modname:
        name = object.__module__ + "." + name
    return name


def isdata(object: Any) -> bool:
    """Check if an object is of a type that probably means it's data."""
    return not (
        inspect.ismodule(object)
        or inspect.isclass(object)
        or inspect.isroutine(object)
        or inspect.isframe(object)
        or inspect.istraceback(object)
        or inspect.iscode(object)
    )


def _is_bound_method(fn: Callable[[Any], Any]) -> bool:
    """
    Returns True if fn is a bound method, regardless of whether
    fn was implemented in Python or in C.
    """
    if inspect.ismethod(fn):
        return True
    if inspect.isbuiltin(fn):
        self = getattr(fn, "__self__", None)
        return not (inspect.ismodule(self) or (self is None))
    return False


def allmethods(cl: type) -> Dict[str, Any]:
    methods = {}
    for key, value in inspect.getmembers(cl, inspect.isroutine):
        methods[key] = 1
    for base in cl.__bases__:
        methods.update(allmethods(base))  # all your base are belong to us
    for key in methods.keys():
        methods[key] = getattr(cl, key)
    return methods


def _split_list(
    s: Sequence[str], predicate: Callable[[Any], bool]
) -> tuple[list[str], list[str]]:
    """Split sequence s via predicate, and return pair ([true], [false]).

    The return value is a 2-tuple of lists,
        ([x for x in s if predicate(x)],
         [x for x in s if not predicate(x)])
    """

    yes = []
    no = []
    for x in s:
        if predicate(x):
            yes.append(x)
        else:
            no.append(x)
    return yes, no


def visiblename(
    name: str, all: Optional[list[str]] = None, obj: Optional[Any] = None
) -> int:
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
        return 0
    # Private names are hidden, but special names are displayed.
    if name.startswith("__") and name.endswith("__"):
        return 1
    # Namedtuples have public fields and methods with a single leading underscore
    if name.startswith("_") and hasattr(obj, "_fields"):
        return True
    if all is not None:
        # only document that which the programmer exported in __all__
        return name in all
    else:
        return not name.startswith("_")


def classify_class_attrs(object: type) -> list[tuple[str, str, str, str]]:
    """Wrap inspect.classify_class_attrs, with fixup for data descriptors."""
    results = []
    for (name, kind, cls, value) in inspect.classify_class_attrs(object):
        if inspect.isdatadescriptor(value):
            kind = "data descriptor"
            if isinstance(value, property) and value.fset is None:
                kind = "readonly property"
        results.append((name, kind, cls, value))
    return results


def sort_attributes(attrs: list, object: Union[TypeLike, type]):
    "Sort the attrs list in-place by _fields and then alphabetically by name"
    # This allows data descriptors to be ordered according
    # to a _fields attribute if present.
    fields = getattr(object, "_fields", [])
    try:
        field_order = {name: i - len(fields) for (i, name) in enumerate(fields)}
    except TypeError:
        field_order = {}
    keyfunc = lambda attr: (field_order.get(attr[0], 0), attr[0])
    attrs.sort(key=keyfunc)


# ----------------------------------------------------- module manipulation


def source_synopsis(file: TextIO) -> Optional[str]:
    line = file.readline()
    while line[:1] == "#" or not line.strip():
        line = file.readline()
        if not line:
            break
    line = line.strip()
    if line[:4] == 'r"""':
        line = line[1:]
    if line[:3] == '"""':
        line = line[3:]
        if line[-1:] == "\\":
            line = line[:-1]
        while not line.strip():
            line = file.readline()
            if not line:
                break
        result = line.split('"""')[0].strip()
    else:
        result = None
    return result


def synopsis(filename: str, cache: dict[str, Any] = {}) -> Optional[str]:
    """Get the one-line summary out of a module file."""
    mtime = os.stat(filename).st_mtime
    lastupdate, result = cache.get(filename, (None, None))
    if lastupdate is None or lastupdate < mtime:
        # Look for binary suffixes first, falling back to source.
        if filename.endswith(tuple(importlib.machinery.BYTECODE_SUFFIXES)):
            loader_cls = importlib.machinery.SourcelessFileLoader
        elif filename.endswith(tuple(importlib.machinery.EXTENSION_SUFFIXES)):
            loader_cls = importlib.machinery.ExtensionFileLoader
        else:
            loader_cls = None
        # Now handle the choice.
        if loader_cls is None:
            # Must be a source file.
            try:
                file = tokenize.open(filename)
            except OSError:
                # module can't be opened, so skip it
                return None
            # text modules can be directly examined
            with file:
                result = source_synopsis(file)
        else:
            # Must be a binary module, which has to be imported.
            loader = loader_cls("__temp__", filename)
            # XXX We probably don't need to pass in the loader here.
            spec = importlib.util.spec_from_file_location(
                "__temp__", filename, loader=loader
            )
            try:
                module = importlib._bootstrap._load(spec)
            except:
                return None
            del sys.modules["__temp__"]
            result = module.__doc__.splitlines()[0] if module.__doc__ else None
        # Cache the result.
        cache[filename] = (mtime, result)
    return result
