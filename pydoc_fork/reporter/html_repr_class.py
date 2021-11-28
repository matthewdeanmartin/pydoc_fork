"""Class for safely making an HTML representation of a Python object."""
import re
from reprlib import Repr
from typing import Any, cast

from pydoc_fork.reporter import inline_styles
from pydoc_fork.reporter.string_utils import cram, replace, stripid


class HTMLRepr(Repr):
    """Class for safely making an HTML representation of a Python object."""

    def __init__(self) -> None:
        """Some maximums"""
        Repr.__init__(self)
        self.maximum_list = self.maximum_tuple = 20
        self.maximum_dict = 10
        self.maximum_string = self.maximum_other = 100

    # pylint: disable=no-self-use
    @staticmethod
    def escape(text: str) -> str:
        """Simple html escaping"""
        result = replace(text, "&", "&amp;", "<", "&lt;", ">", "&gt;")
        # if "&amp;" in result:
        #     print("possible double escape")
        return result

    def repr(self, x: Any) -> str:  # noqa - unhiding could break code?
        """Delegates to Repr.repr"""
        return Repr.repr(self, x)

    def repr1(self, x: Any, level: int) -> str:
        """Not sure, is dead code?"""
        if hasattr(type(x), "__name__"):
            method_name = "repr_" + "_".join(type(x).__name__.split())
            if hasattr(self, method_name):
                return cast(str, getattr(self, method_name)(x, level))
        return self.escape(cram(stripid(repr(x)), self.maximum_other))

    def repr_string(self, x: str, _: int) -> str:
        """Repr, but squash it into a window"""
        test = cram(x, self.maximum_string)
        test_repr = repr(test)
        if "\\" in test and "\\" not in replace(test_repr, r"\\", ""):
            # Backslashes are only literal in the string and are never
            # needed to make any special characters, so show a raw string.
            return "r" + test_repr[0] + self.escape(test) + test_repr[0]

        return re.sub(
            r'((\\[\\abfnrtv\'"]|\\[0-9]..|\\x..|\\u....)+)',
            f'<span style="color:{inline_styles.REPR_COLOR}">' + r"\1" + "</span>",
            self.escape(test_repr),
        )

    repr_str = repr_string

    def repr_instance(self, x: Any, level: int) -> str:
        """Repr, but squash it into a window"""
        # noinspection PyBroadException
        try:
            return self.escape(cram(stripid(repr(x)), self.maximum_string))
        # pylint: disable=broad-except
        except BaseException:
            return self.escape(f"<{x.__class__.__name__} instance>")

    repr_unicode = repr_string
