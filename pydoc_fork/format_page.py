"""
Roughly page and top level containers

[[Page

    [[Document

    ]]
]]
"""
import inspect
import pkgutil
from typing import Any, Dict, Optional

from jinja2 import Environment, PackageLoader, select_autoescape

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.format_class import docclass
from pydoc_fork.format_data import docdata
from pydoc_fork.format_module import docmodule
from pydoc_fork.format_other import docother
from pydoc_fork.format_routine import docroutine
from pydoc_fork.formatter_html import bigsection, modpkglink, multicolumn
from pydoc_fork.jinja_code import JINJA_ENV


def render(title: str, the_object: TypeLike, name: str) -> str:
    """Compose two functions"""
    return page(title, document(the_object, name))


def page(title: str, contents: str) -> str:
    """Format an HTML page.

    This is part of the public API
    """
    template = JINJA_ENV.get_template("page.jinja2")
    result = template.render(title=title, contents=contents)
    return result


#     return f"""\
# <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
# <html><head><title>Python: {title}</title>
# <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
# </head><body bgcolor="#f0f0f8">
# {contents}
# </body></html>"""


def document(the_object: TypeLike, name: str = "", *args: Any) -> str:  # Null safety
    """Generate documentation for an object.
    This also part of the public API of class

    Types of : Module, class, routine, data descriptor, "other" are supported

    Modules ignore 1st name.

    Public API doesn't call with *args
    Args are:
    name, fdict, cdict (name twice?)
    mod, funcs, classes, mdict, the_object
    """
    args = (the_object, name) + args

    # 'try' clause is to attempt to handle the possibility that inspect
    # identifies something in a way that pydoc itself has issues handling;
    # think 'super' and how it is a descriptor (which raises the exception
    # by lacking a __name__ attribute) and an instance.
    # try:
    if inspect.ismodule(the_object):
        return docmodule(the_object)
    if inspect.isclass(the_object):
        return docclass(*args)
    if inspect.isroutine(the_object):
        return docroutine(*args)
    # except AttributeError:
    #     pass  # nosec
    if inspect.isdatadescriptor(the_object):
        return docdata(the_object, name)
    return docother(the_object, name)


# This is page
def index(directory: str, shadowed: Optional[Dict[str, Any]] = None) -> str:
    """Generate an HTML index for a directory of modules."""
    modpkgs = []
    if shadowed is None:
        shadowed = {}
    for _, name, ispkg in pkgutil.iter_modules([directory]):
        if any((0xD800 <= ord(ch) <= 0xDFFF) for ch in name):
            # ignore a module if its name contains a surrogate character
            continue
        modpkgs.append((name, "", ispkg, name in shadowed))
        shadowed[name] = 1

    modpkgs.sort()
    contents = multicolumn(modpkgs, modpkglink)
    return bigsection(directory, "#ffffff", "#ee77aa", contents)
