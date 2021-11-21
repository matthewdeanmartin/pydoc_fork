"""
Generate HTML documentation

[[Page

    [[Document

    ]]
]]



"""
import logging
import os
import re
import sys
import sysconfig
from typing import Any, Callable, Dict, Sequence, Tuple, Union

from pydoc_fork.html_repr_class import HTMLRepr
from pydoc_fork.string_utils import replace

LOGGER = logging.getLogger(__name__)
STDLIB_BASEDIR = sysconfig.get_path("stdlib")

document_internals = False
output_folder = ""

PYTHONDOCS = os.environ.get(
    "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
)

"""Formatter class for HTML documentation."""


# ------------------------------------------- HTML formatting utilities

# monkey patching was messing with mypy-- is this now a redeclare?
def repr(value: Any) -> str:  # noqa - unhiding could break code?
    _repr_instance = HTMLRepr()
    return _repr_instance.repr(value)


def escape(value: Any) -> str:
    _repr_instance = HTMLRepr()
    return _repr_instance.escape(value)


def heading(title: str, fgcol: str, bgcol: str, extras: str = "") -> str:
    """Format a page heading."""
    return """
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="{}">
<td valign=bottom>&nbsp;<br>
<font color="{}" face="helvetica, arial">&nbsp;<br>{}</font></td
><td align=right valign=bottom
><font color="{}" face="helvetica, arial">{}</font></td></tr></table>
""".format(
        bgcol, fgcol, title, fgcol, extras or "&nbsp;"
    )


def section(
    title: str,
    fgcol: str,
    bgcol: str,
    contents: str,
    width: int = 6,
    prelude: str = "",
    marginalia: str = "",
    gap: str = "&nbsp;",
) -> str:
    """Format a section with a heading."""

    # This is only used by docclass

    if marginalia is None:
        marginalia = "<tt>" + "&nbsp;" * width + "</tt>"
    result = """<p>
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="{}">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="{}" face="helvetica, arial">{}</font></td></tr>
""".format(
        bgcol, fgcol, title
    )
    if prelude:
        result = (
            result
            + """
<tr bgcolor="{}"><td rowspan=2>{}</td>
<td colspan=2>{}</td></tr>
<tr><td>{}</td>""".format(
                bgcol, marginalia, prelude, gap
            )
        )
    else:
        result = (
            result
            + """
<tr><td bgcolor="{}">{}</td><td>{}</td>""".format(
                bgcol, marginalia, gap
            )
        )

    return result + '\n<td width="100%%">%s</td></tr></table>' % contents


def bigsection(title: str, *args: Any) -> str:
    """Format a section with a big heading."""
    title = "<big><strong>%s</strong></big>" % title
    return section(title, *args)


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
    return '<table width="100%%" summary="list"><tr>%s</tr></table>' % result


def grey(text: str) -> str:
    return '<font color="#909090">%s</font>' % text


def namelink(name: str, *dicts: Dict[str, str]) -> str:
    """Make a link for an identifier, given name-to-URL mappings."""
    for the_dict in dicts:
        if name in the_dict:
            return f'<a href="{the_dict[name]}">{name}</a>'
    return name


def modpkglink(modpkginfo: Tuple[str, str, str, str]) -> str:
    """Make a link for a module or package to display in an index."""
    name, path, ispackage, shadowed = modpkginfo
    if shadowed:
        return grey(name)
    if path:
        url = f"{path}.{name}.html"
    else:
        url = "%s.html" % name
    if ispackage:
        text = "<strong>%s</strong>&nbsp;(package)" % name
    else:
        text = name
    return f'<a href="{url}">{text}</a>'


def filelink(url: str, path: str) -> str:
    """Make a link to source file."""
    return f'<a href="file:{url}">{path}</a>'


def markup(
    text: str,
    funcs: Dict[str, str] = {},  # noqa - clean up later
    classes: Dict[str, str] = {},  # noqa - clean up later
    methods: Dict[str, str] = {},  # noqa - clean up later
) -> str:
    """Mark up some plain text, given a context of symbols to look for.
    Each context dictionary maps object names to anchor names."""

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

        the_all, scheme, rfc, pep, selfdot, name = match.groups()
        if scheme:
            url = preformat(the_all).replace('"', "&quot;")
            results.append(f'<a href="{url}">{url}</a>')
        elif rfc:
            url = "http://www.rfc-editor.org/rfc/rfc%d.txt" % int(rfc)
            results.append(f'<a href="{url}">{preformat(the_all)}</a>')
        elif pep:
            url = "https://www.python.org/dev/peps/pep-%04d/" % int(pep)
            results.append(f'<a href="{url}">{preformat(the_all)}</a>')
        elif selfdot:
            # Create a link for methods like 'self.method(...)'
            # and use <strong> for attributes like 'self.attr'
            if text[end : end + 1] == "(":
                results.append("self." + namelink(name, methods))
            else:
                results.append("self.<strong>%s</strong>" % name)
        elif text[end : end + 1] == "(":
            results.append(namelink(name, methods, funcs, classes))
        else:
            results.append(namelink(name, classes))
        here = end
    results.append(preformat(text[here:]))
    return "".join(results)


def formatvalue(the_object: Any) -> str:
    """Format an argument default value as text."""
    return grey("=" + repr(the_object))
