"""Class for safely making an HTML representation of a Python object."""
import re
from reprlib import Repr
from typing import Any, cast

from pydoc_fork.string_utils import cram, replace, stripid


class HTMLRepr(Repr):
    """Class for safely making an HTML representation of a Python object."""

    def __init__(self) -> None:
        """Some maximums"""
        Repr.__init__(self)
        self.maxlist = self.maxtuple = 20
        self.maxdict = 10
        self.maxstring = self.maxother = 100

    # pylint: disable=no-self-use
    def escape(self, text: str) -> str:
        """Simple html escaping"""
        return replace(text, "&", "&amp;", "<", "&lt;", ">", "&gt;")

    def repr(self, x: Any) -> str:  # noqa - unhiding could break code?
        """Delegates to Repr.repr"""
        return Repr.repr(self, x)

    def repr1(self, x: Any, level: int) -> str:
        """Not sure, this is dead code"""
        if hasattr(type(x), "__name__"):
            methodname = "repr_" + "_".join(type(x).__name__.split())
            if hasattr(self, methodname):
                return cast(str, getattr(self, methodname)(x, level))
        return self.escape(cram(stripid(repr(x)), self.maxother))

    def repr_string(self, x: str, _: int) -> str:
        """Repr, but squash it into a window"""
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
        """Repr, but squash it into a window"""
        try:
            return self.escape(cram(stripid(repr(x)), self.maxstring))
        # pylint: disable=broad-except
        except BaseException:
            return self.escape(f"<{x.__class__.__name__} instance>")

    repr_unicode = repr_string
