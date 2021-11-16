"""
Generate HTML documenation
"""
# -------------------------------------------- HTML documentation generator
import builtins
import inspect
import os
import pkgutil
import re
import sys
import sysconfig
import urllib.parse
from collections import deque
from reprlib import Repr
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union, cast

from pydoc_fork.custom_types import TypeLike
from pydoc_fork.string_utils import cram, replace, stripid
from pydoc_fork.utils import (
    _is_bound_method,
    _split_list,
    classify_class_attrs,
    classname,
    getdoc,
    isdata,
    sort_attributes,
    visiblename,
)


class HTMLRepr(Repr):
    """Class for safely making an HTML representation of a Python object."""

    def __init__(self) -> None:
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    def escape(self, text: str) -> str:
        return replace(text, "&", "&amp;", "<", "&lt;", ">", "&gt;")

    def repr(self, the_object: Any) -> str:
        return Repr.repr(self, the_object)

    def repr1(self, x: Any, level: int) -> str:
        if hasattr(type(x), "__name__"):
            methodname = "repr_" + "_".join(type(x).__name__.split())
            if hasattr(self, methodname):
                return cast(str, getattr(self, methodname)(x, level))
        return self.escape(cram(stripid(repr(x)), self.maxother))

    def repr_string(self, x: str, _: int) -> str:
        test = cram(x, self.maxstring)
        test_repr = repr(test)
        if "\\" in test and "\\" not in replace(test_repr, r"\\", ""):
            # Backslashes are only literal in the string and are never
            # needed to make any special characters, so show a raw string.
            return "r" + test_repr[0] + self.escape(test) + test_repr[0]
        return re.sub(
            r'((\\[\\abfnrtv\'"]|\\[0-9]..|\\x..|\\u....)+)',
            r'<font color="#c040c0">\1</font>',
            self.escape(test_repr),
        )

    repr_str = repr_string

    def repr_instance(self, x: Any, level: int) -> str:
        try:
            return self.escape(cram(stripid(repr(x)), self.maxstring))
        except:
            return self.escape("<%s instance>" % x.__class__.__name__)

    repr_unicode = repr_string


class HTMLDoc:
    """Generate HTML"""

    def __init__(self) -> None:
        self.document_internals = False
        self.output_folder = ""

    PYTHONDOCS = os.environ.get(
        "PYTHONDOCS", "https://docs.python.org/%d.%d/library" % sys.version_info[:2]
    )

    def document(
        self, the_object: TypeLike, name: str = "", *args: Any  # Null safety
    ) -> str:
        """Generate documentation for an object."""
        args = (the_object, name) + args

        # 'try' clause is to attempt to handle the possibility that inspect
        # identifies something in a way that pydoc itself has issues handling;
        # think 'super' and how it is a descriptor (which raises the exception
        # by lacking a __name__ attribute) and an instance.
        try:
            if inspect.ismodule(the_object):
                return self.docmodule(the_object)
            if inspect.isclass(the_object):
                return self.docclass(*args)
            if inspect.isroutine(the_object):
                return self.docroutine(*args)
        except AttributeError:
            pass
        if inspect.isdatadescriptor(the_object):
            return self.docdata(the_object, name)
        return self.docother(the_object, name)

    """Formatter class for HTML documentation."""

    # ------------------------------------------- HTML formatting utilities

    # monkey patching was messing with mypy
    def repr(self, value: Any) -> str:
        _repr_instance = HTMLRepr()
        return _repr_instance.repr(value)

    def escape(self, value: Any) -> str:
        _repr_instance = HTMLRepr()
        return _repr_instance.escape(value)

    def page(self, title: str, contents: str) -> str:
        """Format an HTML page."""
        return """\
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.0 Transitional//EN">
<html><head><title>Python: {}</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
</head><body bgcolor="#f0f0f8">
{}
</body></html>""".format(
            title, contents
        )

    def heading(self, title: str, fgcol: str, bgcol: str, extras: str = "") -> str:
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
        self,
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

    def bigsection(self, title: str, *args: Any) -> str:
        """Format a section with a big heading."""
        title = "<big><strong>%s</strong></big>" % title
        return self.section(title, *args)

    def preformat(self, text: str) -> str:
        """Format literal preformatted text."""
        text = self.escape(text.expandtabs())
        return replace(
            text, "\n\n", "\n \n", "\n\n", "\n \n", " ", "&nbsp;", "\n", "<br>\n"
        )

    def multicolumn(
        self,
        list: Union[Sequence[Tuple[Any, str, Any, int]], Sequence[Tuple[str, Any]]],
        format: Callable[[Any], str],
        cols: int = 4,
    ) -> str:
        """Format a list of items into a multi-column list."""
        result = ""
        rows = (len(list) + cols - 1) // cols
        for col in range(cols):
            result = result + '<td width="%d%%" valign=top>' % (100 // cols)
            for i in range(rows * col, rows * col + rows):
                if i < len(list):
                    result = result + format(list[i]) + "<br>\n"
            result = result + "</td>"
        return '<table width="100%%" summary="list"><tr>%s</tr></table>' % result

    def grey(self, text: str) -> str:
        return '<font color="#909090">%s</font>' % text

    def namelink(self, name: str, *dicts: Dict[str, str]) -> str:
        """Make a link for an identifier, given name-to-URL mappings."""
        for dict in dicts:
            if name in dict:
                return f'<a href="{dict[name]}">{name}</a>'
        return name

    def classlink(self, the_object: Union[TypeLike, type], modname: str) -> str:
        """Make a link for a class."""
        name, module = the_object.__name__, sys.modules.get(the_object.__module__)
        if hasattr(module, name) and getattr(module, name) is the_object:
            return '<a href="{}.html#{}">{}</a>'.format(
                module.__name__, name, classname(cast(TypeLike, the_object), modname)
            )
        return classname(the_object, modname)

    def modulelink(self, the_object: TypeLike) -> str:
        """Make a link for a module."""
        return f'<a href="{the_object.__name__}.html">{the_object.__name__}</a>'

    def modpkglink(self, modpkginfo: Tuple[str, str, str, str]) -> str:
        """Make a link for a module or package to display in an index."""
        name, path, ispackage, shadowed = modpkginfo
        if shadowed:
            return self.grey(name)
        if path:
            url = f"{path}.{name}.html"
        else:
            url = "%s.html" % name
        if ispackage:
            text = "<strong>%s</strong>&nbsp;(package)" % name
        else:
            text = name
        return f'<a href="{url}">{text}</a>'

    def filelink(self, url: str, path: str) -> str:
        """Make a link to source file."""
        return f'<a href="file:{url}">{path}</a>'

    def markup(
        self,
        text: str,
        custom_escape: Callable[[str], str] = None,
        funcs: Dict[str, str] = {},
        classes: Dict[str, str] = {},
        methods: Dict[str, str] = {},
    ) -> str:
        """Mark up some plain text, given a context of symbols to look for.
        Each context dictionary maps object names to anchor names."""
        escape: Callable[[str], str] = custom_escape or self.escape
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
            results.append(escape(text[here:start]))

            all, scheme, rfc, pep, selfdot, name = match.groups()
            if scheme:
                url = escape(all).replace('"', "&quot;")
                results.append(f'<a href="{url}">{url}</a>')
            elif rfc:
                url = "http://www.rfc-editor.org/rfc/rfc%d.txt" % int(rfc)
                results.append(f'<a href="{url}">{escape(all)}</a>')
            elif pep:
                url = "https://www.python.org/dev/peps/pep-%04d/" % int(pep)
                results.append(f'<a href="{url}">{escape(all)}</a>')
            elif selfdot:
                # Create a link for methods like 'self.method(...)'
                # and use <strong> for attributes like 'self.attr'
                if text[end : end + 1] == "(":
                    results.append("self." + self.namelink(name, methods))
                else:
                    results.append("self.<strong>%s</strong>" % name)
            elif text[end : end + 1] == "(":
                results.append(self.namelink(name, methods, funcs, classes))
            else:
                results.append(self.namelink(name, classes))
            here = end
        results.append(escape(text[here:]))
        return "".join(results)

    # ---------------------------------------------- type-specific routines

    def formattree(
        self, tree: List[Any], modname: str, parent: Optional[Any] = None
    ) -> str:
        """Produce HTML for a class tree as given by inspect.getclasstree()."""
        result = ""
        for entry in tree:
            if type(entry) is type(()):
                class_object, bases = entry
                result = result + '<dt><font face="helvetica, arial">'
                result = result + self.classlink(class_object, modname)
                if bases and bases != (parent,):
                    parents = []
                    for base in bases:
                        parents.append(self.classlink(base, modname))
                    result = result + "(" + ", ".join(parents) + ")"
                result = result + "\n</font></dt>"
            elif type(entry) is type([]):
                result = result + "<dd>\n%s</dd>\n" % self.formattree(
                    entry, modname, class_object
                )
        return "<dl>\n%s</dl>\n" % result

    def docmodule(
        self,
        the_object: TypeLike,
    ) -> str:
        """Produce HTML documentation for a module object."""
        name = the_object.__name__  # ignore the passed-in name

        try:
            all_things = None if self.document_internals else the_object.__all__
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
            output_folder_path = os.path.normcase(os.path.abspath(self.output_folder))
            path = os.path.relpath(path, output_folder_path).replace("\\", "/")
            # end MR
            url = urllib.parse.quote(path)
            # MR
            filelink = self.filelink(path, path)
        except TypeError:
            filelink = "(built-in)"
        info = []
        if hasattr(the_object, "__version__"):
            version = str(the_object.__version__)
            if version[:11] == "$" + "Revision: " and version[-1:] == "$":
                version = version[11:-1].strip()
            info.append("version %s" % self.escape(version))
        if hasattr(the_object, "__date__"):
            info.append(self.escape(str(the_object.__date__)))
        if info:
            head = head + " (%s)" % ", ".join(info)
        docloc = self.getdocloc(the_object)
        if docloc is not None:
            docloc = '<br><a href="%(docloc)s">Module Reference</a>' % locals()
        else:
            docloc = ""
        result = self.heading(
            head, "#ffffff", "#7799ee", '<a href=".">index</a><br>' + filelink + docloc
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

        doc = self.markup(getdoc(the_object), self.preformat, fdict, cdict)
        doc = doc and "<tt>%s</tt>" % doc
        result = result + "<p>%s</p>\n" % doc

        if hasattr(the_object, "__path__"):
            modpkgs = []
            for importer, modname, ispkg in pkgutil.iter_modules(the_object.__path__):
                modpkgs.append((modname, name, ispkg, 0))
            modpkgs.sort()
            contents_string = self.multicolumn(modpkgs, self.modpkglink)
            result = result + self.bigsection(
                "Package Contents", "#ffffff", "#aa55cc", contents_string
            )
        elif modules:
            contents_string = self.multicolumn(modules, lambda t: self.modulelink(t[1]))
            result = result + self.bigsection(
                "Modules", "#ffffff", "#aa55cc", contents_string
            )

        if classes:
            class_list = [value for (key, value) in classes]
            # MR: boolean type safety
            contents_list = [
                self.formattree(inspect.getclasstree(class_list, True), name)
            ]
            for key, value in classes:
                contents_list.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                "Classes", "#ffffff", "#ee77aa", " ".join(contents_list)
            )
        if funcs:
            contents_list = []
            for key, value in funcs:
                contents_list.append(self.document(value, key, name, fdict, cdict))
            result = result + self.bigsection(
                "Functions", "#ffffff", "#eeaa77", " ".join(contents_list)
            )
        if data:
            contents_list = []
            for key, value in data:
                contents_list.append(self.document(value, key))
            result = result + self.bigsection(
                "Data", "#ffffff", "#55aa55", "<br>\n".join(contents_list)
            )
        if hasattr(the_object, "__author__"):
            contents = self.markup(str(the_object.__author__), self.preformat)
            result = result + self.bigsection("Author", "#ffffff", "#7799ee", contents)
        if hasattr(the_object, "__credits__"):
            contents = self.markup(str(the_object.__credits__), self.preformat)
            result = result + self.bigsection("Credits", "#ffffff", "#7799ee", contents)

        return result

    def docclass(
        self,
        the_object: TypeLike,
        name: str = "",
        mod: str = "",
        funcs: Dict[str, str] = {},
        classes: Dict[str, str] = {},
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
                push("<dd>%s</dd>\n" % self.classlink(base, the_object.__module__))
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
                    except Exception:
                        # Some descriptors may meet a failure in their __get__.
                        # (bug #1785)
                        push(
                            self.docdata(
                                value,
                                name,
                                # mod, unused
                            )
                        )
                    else:
                        push(
                            self.document(
                                value, name, mod, funcs, classes, mdict, the_object
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
                        self.docdata(
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
                    base = self.docother(
                        getattr(the_object, name),
                        name,
                        # mod ignored
                    )
                    found_doc = getdoc(value)
                    if not found_doc:
                        push("<dl><dt>%s</dl>\n" % base)
                    else:
                        found_doc = self.markup(
                            getdoc(value), self.preformat, funcs, classes, mdict
                        )
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
            except Exception:
                # Some descriptors may meet a failure in their __get__.
                # (bug #1785)
                pass
            try:
                # The value may not be hashable (e.g., a data attr with
                # a dict or list value).
                mdict[value] = anchor
            except TypeError:
                pass

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
                tag = "inherited from %s" % self.classlink(
                    thisclass, the_object.__module__
                )
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
            is_data_descriptor: Callable[[Any], Any] = (
                lambda t: t[1] == "data descriptor"
            )
            attrs = spilldescriptors(
                "Data descriptors %s" % tag, attrs, is_data_descriptor
            )
            is_data: Callable[[Any], Any] = lambda t: t[1] == "data"
            attrs = spilldata("Data and other attributes %s" % tag, attrs, is_data)
            assert attrs == []
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
                parents.append(self.classlink(base, the_object.__module__))
            title = title + "(%s)" % ", ".join(parents)

        decl = ""
        try:
            signature = inspect.signature(the_object)
        except (ValueError, TypeError):
            signature = None
        if signature:
            argspec = str(signature)
            if argspec and argspec != "()":
                decl = name + self.escape(argspec) + "\n\n"

        doc = getdoc(the_object)
        if decl:
            doc = decl + (doc or "")
        doc = self.markup(doc, self.preformat, funcs, classes, mdict)
        doc = doc and "<tt>%s<br>&nbsp;</tt>" % doc

        return self.section(title, "#000000", "#ffc8d8", contents_as_string, 3, doc)

    def formatvalue(self, the_object: Any) -> str:
        """Format an argument default value as text."""
        return self.grey("=" + self.repr(the_object))

    def docroutine(
        self,
        the_object: TypeLike,
        name: str = "",
        mod: str = "",
        funcs: Dict[str, Any] = {},
        classes: Dict[str, Any] = {},
        methods: Dict[str, Any] = {},
        cl: Optional[TypeLike] = None,
    ) -> str:
        """Produce HTML documentation for a function or method object."""
        realname = the_object.__name__
        name = name or realname
        anchor = (cl and cl.__name__ or "") + "-" + name
        note = ""
        skipdocs = 0
        if _is_bound_method(the_object):
            imclass = the_object.__self__.__class__
            if cl:
                if imclass is not cl:
                    note = " from " + self.classlink(imclass, mod)
            else:
                if the_object.__self__ is not None:
                    note = " method of %s instance" % self.classlink(
                        the_object.__self__.__class__, mod
                    )
                else:
                    note = " unbound %s method" % self.classlink(imclass, mod)

        if inspect.iscoroutinefunction(the_object) or inspect.isasyncgenfunction(
            the_object
        ):
            asyncqualifier = "async "
        else:
            asyncqualifier = ""

        if name == realname:
            title = f'<a name="{anchor}"><strong>{realname}</strong></a>'
        else:
            if cl and inspect.getattr_static(cl, realname, []) is the_object:
                reallink = '<a href="#{}">{}</a>'.format(
                    cl.__name__ + "-" + realname, realname
                )
                skipdocs = 1
            else:
                reallink = realname
            title = '<a name="{}"><strong>{}</strong></a> = {}'.format(
                anchor, name, reallink
            )
        argspec = None
        if inspect.isroutine(the_object):
            try:
                signature = inspect.signature(the_object)
            except (ValueError, TypeError):
                signature = None
            if signature:
                argspec = str(signature)
                if realname == "<lambda>":
                    title = "<strong>%s</strong> <em>lambda</em> " % name
                    # XXX lambda's won't usually have func_annotations['return']
                    # since the syntax doesn't support but it is possible.
                    # So removing parentheses isn't truly safe.
                    argspec = argspec[1:-1]  # remove parentheses
        if not argspec:
            argspec = "(...)"

        decl = (
            asyncqualifier
            + title
            + self.escape(argspec)
            + (note and self.grey('<font face="helvetica, arial">%s</font>' % note))
        )

        if skipdocs:
            return "<dl><dt>%s</dt></dl>\n" % decl

        doc = self.markup(getdoc(the_object), self.preformat, funcs, classes, methods)
        doc = doc and "<dd><tt>%s</tt></dd>" % doc
        return f"<dl><dt>{decl}</dt>{doc}</dl>\n"

    def docdata(
        self,
        the_object: TypeLike,
        name: str = "",  # Null safety
        # mod: Optional[str] = None,
        # cl: Optional[str] = None,
    ) -> str:
        """Produce html documentation for a data descriptor."""
        results: List[str] = []
        push = results.append

        if name:
            push("<dl><dt><strong>%s</strong></dt>\n" % name)
        doc = self.markup(getdoc(the_object), self.preformat)
        if doc:
            push("<dd><tt>%s</tt></dd>\n" % doc)
        push("</dl>\n")

        return "".join(results)

    docproperty = docdata

    def docother(
        self,
        the_object: TypeLike,
        name: str = "",  # Null safety,
        # mod: Optional[str] = None,
        # *ignored,
    ) -> str:
        """Produce HTML documentation for a data object."""
        lhs = name and "<strong>%s</strong> = " % name or ""
        return lhs + self.repr(the_object)

    def index(self, directory: str, shadowed: Optional[Dict[str, Any]] = None) -> str:
        """Generate an HTML index for a directory of modules."""
        modpkgs = []
        if shadowed is None:
            shadowed = {}
        for importer, name, ispkg in pkgutil.iter_modules([directory]):
            if any((0xD800 <= ord(ch) <= 0xDFFF) for ch in name):
                # ignore a module if its name contains a surrogate character
                continue
            modpkgs.append((name, "", ispkg, name in shadowed))
            shadowed[name] = 1

        modpkgs.sort()
        contents = self.multicolumn(modpkgs, self.modpkglink)
        return self.bigsection(directory, "#ffffff", "#ee77aa", contents)

    def getdocloc(
        self, the_object: TypeLike, basedir: str = sysconfig.get_path("stdlib")
    ) -> Optional[str]:
        """Return the location of module docs or None"""

        try:
            file = inspect.getabsfile(cast(type, the_object))
        except TypeError:
            file = "(built-in)"

        # null safety problem here
        doc_loc: Optional[str] = os.environ.get("PYTHONDOCS", self.PYTHONDOCS)

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
