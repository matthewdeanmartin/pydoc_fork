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

DOCUMENT_INTERNALS = False
OUTPUT_FOLDER = ""

PYTHONDOCS = os.environ.get(
    "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
)

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
    return f"""
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="heading">
<tr bgcolor="{bgcol}">
<td valign=bottom>&nbsp;<br>
<font color="{fgcol}" face="helvetica, arial">&nbsp;<br>{title}</font></td
><td align=right valign=bottom
><font color="{fgcol}" face="helvetica, arial">{extras or '&nbsp;'}</font></td></tr></table>
"""


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

    # This is only used by docclass

    if marginalia is None:
        marginalia = "<tt>" + "&nbsp;" * width + "</tt>"
    result = f"""<p>
<table width="100%" cellspacing=0 cellpadding=2 border=0 summary="section">
<tr bgcolor="{bgcol}">
<td colspan=3 valign=bottom>&nbsp;<br>
<font color="{fgcol}" face="helvetica, arial">{title}</font></td></tr>
"""
    if prelude:
        result = (
            result
            + f"""
<tr bgcolor="{bgcol}"><td rowspan=2>{marginalia}</td>
<td colspan=2>{prelude}</td></tr>
<tr><td>{gap}</td>"""
        )
    else:
        result = (
            result
            + f"""
<tr><td bgcolor="{bgcol}">{marginalia}</td><td>{gap}</td>"""
        )

    return result + f'\n<td width="100%%">{contents}</td></tr></table>'


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


def grey(text: str) -> str:
    """Wrap in grey"""
    return f'<font color="#909090">{text}</font>'


def namelink(name: str, *dicts: Dict[str, str]) -> str:
    """Make a link for an identifier, given name-to-URL mappings."""
    for the_dict in dicts:
        if name in the_dict:
            return f'<a href="{the_dict[name]}">{name}</a>'
    # LOGGER.warning(f"Failed to find link for {name}")
    return name


def modpkglink(modpkginfo: Tuple[str, str, str, str]) -> str:
    """Make a link for a module or package to display in an index."""
    name, path, ispackage, shadowed = modpkginfo
    if shadowed:
        return grey(name)
    if path:
        url = f"{path}.{name}.html"
    else:
        url = f"{name}.html"
    if ispackage:
        text = f"<strong>{name}</strong>&nbsp;(package)"
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
                results.append(f"self.<strong>{name}</strong>")
        elif text[end : end + 1] == "(":
            results.append(namelink(name, methods, funcs, classes))
        else:
            # This assumes everything else is a class!!
            results.append(namelink(name, classes))
        here = end
    results.append(preformat(text[here:]))
    return "".join(results)


# dead code
# def formatvalue(the_object: Any) -> str:
#     """Format an argument default value as text."""
#     return grey("=" + html_repr(the_object))
