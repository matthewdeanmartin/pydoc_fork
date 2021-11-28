"""
Roughly a UI component for modules
"""
import inspect
import os
import pkgutil
import sys
from typing import Optional, cast

from pydoc_fork import settings
from pydoc_fork.inspector.custom_types import TypeLike
from pydoc_fork.inspector.utils import getdoc, isdata, visiblename
from pydoc_fork.reporter import inline_styles
from pydoc_fork.reporter.format_class import format_tree
from pydoc_fork.reporter.formatter_html import (
    STDLIB_BASEDIR,
    bigsection,
    escape,
    file_link,
    heading,
    markup,
    module_package_link,
    multicolumn,
)


def getdocloc(the_object: TypeLike, basedir: str = STDLIB_BASEDIR) -> Optional[str]:
    """Return the location of module docs or None"""
    try:
        file = inspect.getabsfile(cast(type, the_object))
    except TypeError:
        file = "(built-in)"

    basedir = os.path.normcase(basedir)
    is_known_stdlib = the_object.__name__ in (
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
    is_module = isinstance(the_object, type(os))
    is_in_pythons_folder = file.startswith(basedir) and not file.startswith(
        os.path.join(basedir, "site-packages")
    )
    # # This is nasty special case coding, how many more special cases are there?
    # is_exception =the_object.__name__ in ("xml.etree", "test.pydoc_mod")
    # # special case for etree
    # "https://docs.python.org/3/library/xml.etree.elementtree.html"

    if (
        is_module
        and (is_known_stdlib or is_in_pythons_folder)
        and settings.PREFER_DOCS_PYTHON_ORG
    ):
        if settings.PYTHONDOCS.startswith(("http://", "https://")):
            doc_loc = (
                f"{settings.PYTHONDOCS.rstrip('/')}/{the_object.__name__.lower()}.html"
            )
        else:
            doc_loc = os.path.join(
                settings.PYTHONDOCS, the_object.__name__.lower() + ".html"
            )
    else:
        doc_loc = None
    return doc_loc


def modulelink(the_object: TypeLike) -> str:
    """Make a link for a module."""
    url = f"{the_object.__name__}.html"
    internet_link = getdocloc(the_object)

    if internet_link and settings.PREFER_DOCS_PYTHON_ORG:
        url = internet_link
    # BUG: doesn't take into consideration an alternate base
    if not internet_link:
        settings.MENTIONED_MODULES.add((the_object, the_object.__name__))
    return f'<a href="{url}">{the_object.__name__}</a>'


def docmodule(
    the_object: TypeLike,
) -> str:
    """Produce HTML documentation for a module object."""
    # circular ref
    from pydoc_fork.reporter.format_page import document

    name = the_object.__name__

    try:
        all_things = None if settings.DOCUMENT_INTERNALS else the_object.__all__
    except AttributeError:
        all_things = None
    parts = name.split(".")
    links = []
    for i in range(len(parts) - 1):
        link_url = ".".join(parts[: i + 1])
        link_text = parts[i]
        links.append(
            f'<a href="{link_url}.html"><span style="color:{inline_styles.MODULE_LINK}">{link_text}</span></a>'
        )
    linked_name = ".".join(links + parts[-1:])
    head = f"<big><big><strong>{linked_name}</strong></big></big>"
    try:
        path = inspect.getabsfile(cast(type, the_object))
        # MR : Make relative
        output_folder_path = os.path.normcase(os.path.abspath(settings.OUTPUT_FOLDER))
        path = os.path.relpath(path, output_folder_path).replace("\\", "/")
        # end MR
        # uh, oh, forgot why I wrote this
        # url = urllib.parse.quote(path)
        # MR
        file_link_text = file_link(path, path)
    except TypeError:
        file_link_text = "(built-in)"
    info = []
    # TODO: Include the rest of the meta data
    if hasattr(the_object, "__version__"):
        version = str(the_object.__version__)
        if version[:11] == "$" + "Revision: " and version[-1:] == "$":
            version = version[11:-1].strip()
        info.append(f"version {escape(version)}")
    if hasattr(the_object, "__date__"):
        info.append(escape(str(the_object.__date__)))
    if info:
        head = head + f" ({', '.join(info)})"
    document_location = getdocloc(the_object)
    if document_location is not None:
        # Was this just a bug? document_location/locals?
        # document_location = '<br><a href="%(docloc)s">Module Reference</a>' % locals()
        document_location = f'<br><a href="{document_location}">Module Reference</a>'
    else:
        document_location = ""
    result = heading(
        head,
        "#ffffff",
        "#7799ee",
        '<a href=".">index</a><br>' + file_link_text + document_location,
    )

    # this will get `import foo` but ignore `from foo import bar`
    # And bar gets no doc string love either!
    modules = inspect.getmembers(the_object, inspect.ismodule)

    for to_remove in settings.SKIP_MODULES:
        for module_info in modules:
            candidate_module, _ = module_info
            if candidate_module == to_remove:
                try:
                    modules.remove(module_info)
                except ValueError:
                    pass
    modules_by_import_from = set()
    classes, class_dict = [], {}
    for key, value in inspect.getmembers(the_object, inspect.isclass):
        _class_module = inspect.getmodule(value)
        if _class_module and _class_module is not the_object:
            if _class_module.__name__ not in settings.SKIP_MODULES:
                modules_by_import_from.add((None, _class_module))
                settings.MENTIONED_MODULES.add((_class_module, _class_module.__name__))
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        if (
            # TODO put doc internals switch here
            # all_things is not None or
            (inspect.getmodule(value) or the_object)
            is the_object
        ):
            if visiblename(key, all_things, the_object):
                classes.append((key, value))
                class_dict[key] = class_dict[value] = "#" + key
    for key, value in classes:
        for base in value.__bases__:
            key, modname = base.__name__, base.__module__
            module = sys.modules.get(modname)
            if (
                modname != name
                and module
                and hasattr(module, key)
                and getattr(module, key) is base
                and key not in class_dict
            ):
                class_dict[key] = class_dict[base] = modname + ".html#" + key
    funcs, function_dict = [], {}
    for key, value in inspect.getmembers(the_object, inspect.isroutine):
        # if __all__ exists, believe it.  Otherwise use old heuristic.
        _func_module = inspect.getmodule(value)
        # why does this sometimes return no module?
        if _func_module and _func_module is not the_object:
            if _func_module.__name__ not in settings.SKIP_MODULES:
                modules_by_import_from.add((None, _func_module))
                settings.MENTIONED_MODULES.add((_func_module, _func_module.__name__))
        if (
            True
            # TODO put doc internals switch here
            # all_things is not None or # __all__ as scope limiter
            # inspect.isbuiltin(value)  # thing w/o module
            # or inspect.getmodule(value) is the_object # from foo import bar
        ) and visiblename(key, all_things, the_object):
            funcs.append((key, value))
            function_dict[key] = "#-" + key
            if inspect.isfunction(value):
                function_dict[value] = function_dict[key]
    data = []
    for key, value in inspect.getmembers(the_object, isdata):
        if inspect.getmodule(type(value)).__name__ in settings.SKIP_MODULES:
            continue
        if visiblename(key, all_things, the_object):
            data.append((key, value))

    doc = markup(getdoc(the_object), function_dict, class_dict)
    doc = doc and f"<tt>{doc}</tt>"
    result = result + f"<p>{doc}</p>\n"

    if hasattr(the_object, "__path__"):
        module_packages = []
        for _, modname, is_package in pkgutil.iter_modules(the_object.__path__):
            if modname not in settings.SKIP_MODULES:
                module_packages.append((modname, name, is_package, 0))
        module_packages.sort()
        contents_string = multicolumn(module_packages, module_package_link)
        result = result + bigsection(
            "Package Contents", "#ffffff", "#aa55cc", contents_string
        )
    elif modules:
        contents_string = multicolumn(modules, lambda t: modulelink(t[1]))
        result = result + bigsection("Modules", "#ffffff", "#aa55cc", contents_string)

    if modules_by_import_from:
        contents_string = multicolumn(
            list(modules_by_import_from), lambda t: modulelink(list(t)[1])
        )
        result = result + bigsection(
            "`from` Modules", "#ffffff", "#aa55cc", contents_string
        )

    if classes:
        class_list = [value for (key, value) in classes]
        # MR: boolean type safety
        contents_list = [format_tree(inspect.getclasstree(class_list, True), name)]
        for key, value in classes:
            contents_list.append(document(value, key, name, function_dict, class_dict))
        result = result + bigsection(
            "Classes", "#ffffff", "#ee77aa", " ".join(contents_list)
        )
    if funcs:
        contents_list = []
        for key, value in funcs:
            contents_list.append(document(value, key, name, function_dict, class_dict))
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
