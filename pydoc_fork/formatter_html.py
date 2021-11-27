"""
Roughly components
"""
import logging
import re
import sysconfig
from enum import Enum
from typing import Any, Callable, Dict, Sequence, Tuple, Union

import markdown

from pydoc_fork import inline_styles
from pydoc_fork.all_found import MENTIONED_MODULES
from pydoc_fork.html_repr_class import HTMLRepr
from pydoc_fork.jinja_code import JINJA_ENV
from pydoc_fork.module_utils import ErrorDuringImport
from pydoc_fork.rst_support import rst_to_html
from pydoc_fork.string_utils import replace
from pydoc_fork.utils import resolve

LOGGER = logging.getLogger(__name__)
STDLIB_BASEDIR = sysconfig.get_path("stdlib")

"""Formatter class for HTML documentation."""


# monkey patching was messing with mypy-- is this now a redeclare?
def html_repr(value: Any) -> str:  # noqa - unhiding could break code?
    """Turn method into function"""
    _repr_instance = HTMLRepr()
    return _repr_instance.repr(value)


def escape(value: Any) -> str:
    """HTML safe repr and escape"""
    _repr_instance = HTMLRepr()
    result = _repr_instance.escape(value)
    if "&amp;gt;" in result:
        print("possible double escape")
    return result


def heading(title: str, fgcol: str, bgcol: str, extras: str = "") -> str:
    """Format a page heading."""
    template = JINJA_ENV.get_template("heading.jinja2")
    return template.render(title=title, fgcol=fgcol, bgcol=bgcol, extras=extras)


def section(
    title: str,
    fgcol: str,
    bgcol: str,
    contents: str,
    width: int = 6,  # used by marginalia?
    prelude: str = "",
    marginalia: str = "",  # not used
    gap: str = "&nbsp;",  # not used
) -> str:
    """Format a section with a heading."""
    if marginalia is None:
        marginalia = "<tt>" + "&nbsp;" * width + "</tt>"
    template = JINJA_ENV.get_template("section.jinja2")
    return template.render(
        title=title,
        fgcol=fgcol,
        bgcol=bgcol,
        marginalia=marginalia,
        prelude=prelude,
        contents=contents,
        gap=gap,
    )


def bigsection(
    title: str,
    fgcol: str,
    bgcol: str,
    contents: str,
    width: int = 6,  # used by marginalia?
    prelude: str = "",
    marginalia: str = "",  # not used
    gap: str = "&nbsp;",  # not used
) -> str:
    """Format a section with a big heading."""
    title = f"<big><strong>{title}</strong></big>"
    # prefer explicit interfaces over secret hidden ones
    return section(title, fgcol, bgcol, contents, width, prelude, marginalia, gap)


def preformat(text: str) -> str:
    """Format literal preformatted text."""
    text = escape(text.expandtabs())
    return replace(
        text, "\n\n", "\n \n", "\n\n", "\n \n", " ", "&nbsp;", "\n", "<br>\n"
    )


def multicolumn(
    the_list: Union[Sequence[Tuple[Any, str, Any, int]], Sequence[Tuple[str, Any]]],
    the_format: Callable[[Any], str],
    cols: int = 4,
) -> str:
    """Format a list of items into a multi-column list."""
    result = ""
    rows = (len(the_list) + cols - 1) // cols
    for col in range(cols):
        result = result + '<td width="%d%%" valign=top>' % (100 // cols)
        for i in range(rows * col, rows * col + rows):
            if i < len(the_list):
                result = result + the_format(the_list[i]) + "<br>\n"
        result = result + "</td>"
    return f'<table width="100%%" summary="list"><tr>{result}</tr></table>'


def disabled_text(text: str) -> str:
    """Wrap in grey"""
    return f'<span style="color:{inline_styles.DISABLED_TEXT}">{text}</span>'


def namelink(name: str, *dicts: Dict[str, str]) -> str:
    """Make a link for an identifier, given name-to-URL mappings."""
    for the_dict in dicts:
        if name in the_dict:
            return f'<a href="{the_dict[name]}">{name}</a>'
    # LOGGER.warning(f"Failed to find link for {name}")
    return name


def module_package_link(module_package_info: Tuple[str, str, str, str]) -> str:
    """Make a link for a module or package to display in an index."""
    name, path, ispackage, shadowed = module_package_info
    try:
        MENTIONED_MODULES.add((resolve(path + "." + name)[0], name))
    except (ErrorDuringImport, ImportError):
        print(f"Can't import {name}, won't doc")
    if shadowed:
        return disabled_text(name)
    if path:
        url = f"{path}.{name}.html"
    else:
        url = f"{name}.html"
    if ispackage:
        text = f"<strong>{name}</strong>&nbsp;(package)"
    else:
        text = name
    return f'<a href="{url}">{text}</a>'


def file_link(url: str, path: str) -> str:
    """Make a link to source file."""
    return f'<a href="file:{url}">{path}</a>'


class MarkupSyntax(Enum):
    Nothing = 0
    RST = 1
    Markdown = 2


def markup(
    text: str,
    funcs: Dict[str, str] = {},  # noqa - clean up later
    classes: Dict[str, str] = {},  # noqa - clean up later
    methods: Dict[str, str] = {},  # noqa - clean up later
) -> str:
    """
    Replace all linkable things with links of appropriate syntax.

    Handle either an adhoc markup language, or RST or Markdown.
    funcs, classes, methods are name/symbol to URL maps.
    """

    syntax = MarkupSyntax.Nothing

    def nothing(_: str) -> str:
        """Does nothing"""
        return _

    if syntax == MarkupSyntax.Nothing:
        markup_to_html = nothing
        # make_html_link =
    elif syntax == MarkupSyntax.RST:
        preformat = nothing
        markup_to_html = rst_to_html
        # make_rst_link =
    elif syntax == MarkupSyntax.Markdown:
        preformat = lambda _: _
        markup_to_html = markdown.markdown
        # make_markdown_link =
    else:
        raise NotImplemented()

    results = []
    here = 0
    pattern = re.compile(
        r"\b((http|https|ftp)://\S+[\w/]|"
        r"RFC[- ]?(\d+)|"
        r"PEP[- ]?(\d+)|"
        r"(self\.)?(\w+))"
    )
    while True:
        match = pattern.search(text, here)
        if not match:
            break
        start, end = match.span()
        results.append(preformat(text[here:start]))

        the_all, scheme, rfc, pep, self_dot, name = match.groups()
        if scheme:
            # Hyperlink actual urls
            url = preformat(the_all).replace('"', "&quot;")
            results.append(f'<a href="{url}">{url}</a>')
        elif rfc:
            url = "https://www.rfc-editor.org/rfc/rfc%d.txt" % int(rfc)
            results.append(f'<a href="{url}">{preformat(the_all)}</a>')
        elif pep:
            url = "https://www.python.org/dev/peps/pep-%04d/" % int(pep)
            results.append(f'<a href="{url}">{preformat(the_all)}</a>')
        elif self_dot:
            # Create a link for methods like 'self.method(...)'
            # and use <strong> for attributes like 'self.attr'
            if text[end : end + 1] == "(":
                results.append("self." + namelink(name, methods))
            else:
                results.append(f"self.<strong>{name}</strong>")
        elif text[end : end + 1] == "(":
            results.append(namelink(name, methods, funcs, classes))
        else:
            # This assumes everything else is a class!!
            results.append(namelink(name, classes))
        here = end
    # plain text with links to HTML
    results.append(preformat(text[here:]))
    rejoined_semi_html = "".join(results)
    return markup_to_html(rejoined_semi_html)
