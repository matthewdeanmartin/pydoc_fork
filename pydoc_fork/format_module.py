"""
Roughly a UI component for modules
"""
import inspect
import os
import pkgutil
import sys
import urllib.parse
from typing import Optional, cast

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.format_class import formattree
from pydoc_fork.formatter_html import (
    PYTHONDOCS,
    STDLIB_BASEDIR,
    bigsection,
    document_internals,
    escape,
    filelink,
    heading,
    markup,
    modpkglink,
    multicolumn,
    output_folder,
)
from pydoc_fork.utils import getdoc, isdata, visiblename


def getdocloc(the_object: TypeLike, basedir: str = STDLIB_BASEDIR) -> Optional[str]:
    """Return the location of module docs or None"""

    try:
        file = inspect.getabsfile(cast(type, the_object))
    except TypeError:
        file = "(built-in)"

    # null safety problem here
    doc_loc: Optional[str] = os.environ.get("PYTHONDOCS", PYTHONDOCS)

    basedir = os.path.normcase(basedir)
    if (
        isinstance(the_object, type(os))
        and (
            the_object.__name__
            in (
                "errno",
                "exceptions",
                "gc",
                "imp",
                "marshal",
                "posix",
                "signal",
                "sys",
                "_thread",
                "zipimport",
            )
            or (
                file.startswith(basedir)
                and not file.startswith(os.path.join(basedir, "site-packages"))
            )
        )
        and the_object.__name__ not in ("xml.etree", "test.pydoc_mod")
    ):
        if doc_loc.startswith(("http://", "https://")):
            doc_loc = "{}/{}.html".format(
                doc_loc.rstrip("/"), the_object.__name__.lower()
            )
        else:
            doc_loc = os.path.join(doc_loc, the_object.__name__.lower() + ".html")
    else:
        doc_loc = None
    return doc_loc


def modulelink(the_object: TypeLike) -> str:
    """Make a link for a module."""
    return f'<a href="{the_object.__name__}.html">{the_object.__name__}</a>'


def docmodule(
    the_object: TypeLike,
) -> str:
    """Produce HTML documentation for a module object."""
    # circular ref
    from pydoc_fork.format_page import document

    name = the_object.__name__

    try:
        all_things = None if document_internals else the_object.__all__
    except AttributeError:
        all_things = None
    parts = name.split(".")
    links = []
    for i in range(len(parts) - 1):
        links.append(
            '<a href="%s.html"><font color="#ffffff">%s</font></a>'
            % (".".join(parts[: i + 1]), parts[i])
        )
    linkedname = ".".join(links + parts[-1:])
    head = "<big><big><strong>%s</strong></big></big>" % linkedname
    try:
        path = inspect.getabsfile(cast(type, the_object))
        # MR : Make relative
        output_folder_path = os.path.normcase(os.path.abspath(output_folder))
        path = os.path.relpath(path, output_folder_path).replace("\\", "/")
        # end MR
        url = urllib.parse.quote(path)
        # MR
        filelink_text = filelink(path, path)
    except TypeError:
        filelink_text = "(built-in)"
    info = []
    if hasattr(the_object, "__version__"):
        version = str(the_object.__version__)
        if version[:11] == "$" + "Revision: " and version[-1:] == "$":
            version = version[11:-1].strip()
        info.append("version %s" % escape(version))
    if hasattr(the_object, "__date__"):
        info.append(escape(str(the_object.__date__)))
    if info:
        head = head + " (%s)" % ", ".join(info)
    docloc = getdocloc(the_object)
    if docloc is not None:
        docloc = '<br><a href="%(docloc)s">Module Reference</a>' % locals()
    else:
        docloc = ""
    result = heading(
        head, "#ffffff", "#7799ee", '<a href=".">index</a><br>' + filelink_text + docloc
    )

    modules = inspect.getmembers(the_object, inspect.ismodule)

    classes, cdict = [], {}
    for key, value in inspect.getmembers(the_object, inspect.isclass):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (
            all_things is not None
            or (inspect.getmodule(value) or the_object) is the_object
        ):
            if visiblename(key, all_things, the_object):
                classes.append((key, value))
                cdict[key] = cdict[value] = "#" + key
    for key, value in classes:
        for base in value.__bases__:
            key, modname = base.__name__, base.__module__
            module = sys.modules.get(modname)
            if (
                modname != name
                and module
                and hasattr(module, key)
                and getattr(module, key) is base
                and key not in cdict
            ):
                cdict[key] = cdict[base] = modname + ".html#" + key
    funcs, fdict = [], {}
    for key, value in inspect.getmembers(the_object, inspect.isroutine):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (
            all_things is not None
            or inspect.isbuiltin(value)
            or inspect.getmodule(value) is the_object
        ) and visiblename(key, all_things, the_object):
            funcs.append((key, value))
            fdict[key] = "#-" + key
            if inspect.isfunction(value):
                fdict[value] = fdict[key]
    data = []
    for key, value in inspect.getmembers(the_object, isdata):
        if visiblename(key, all_things, the_object):
            data.append((key, value))

    doc = markup(getdoc(the_object), fdict, cdict)
    doc = doc and "<tt>%s</tt>" % doc
    result = result + "<p>%s</p>\n" % doc

    if hasattr(the_object, "__path__"):
        modpkgs = []
        for _, modname, ispkg in pkgutil.iter_modules(the_object.__path__):
            modpkgs.append((modname, name, ispkg, 0))
        modpkgs.sort()
        contents_string = multicolumn(modpkgs, modpkglink)
        result = result + bigsection(
            "Package Contents", "#ffffff", "#aa55cc", contents_string
        )
    elif modules:
        contents_string = multicolumn(modules, lambda t: modulelink(t[1]))
        result = result + bigsection("Modules", "#ffffff", "#aa55cc", contents_string)

    if classes:
        class_list = [value for (key, value) in classes]
        # MR: boolean type safety
        contents_list = [formattree(inspect.getclasstree(class_list, True), name)]
        for key, value in classes:

            contents_list.append(document(value, key, name, fdict, cdict))
        result = result + bigsection(
            "Classes", "#ffffff", "#ee77aa", " ".join(contents_list)
        )
    if funcs:
        contents_list = []
        for key, value in funcs:

            contents_list.append(document(value, key, name, fdict, cdict))
        result = result + bigsection(
            "Functions", "#ffffff", "#eeaa77", " ".join(contents_list)
        )
    if data:
        contents_list = []
        for key, value in data:

            contents_list.append(document(value, key))
        result = result + bigsection(
            "Data", "#ffffff", "#55aa55", "<br>\n".join(contents_list)
        )
    if hasattr(the_object, "__author__"):
        contents = markup(str(the_object.__author__))
        result = result + bigsection("Author", "#ffffff", "#7799ee", contents)
    if hasattr(the_object, "__credits__"):
        contents = markup(str(the_object.__credits__))
        result = result + bigsection("Credits", "#ffffff", "#7799ee", contents)

    return result
