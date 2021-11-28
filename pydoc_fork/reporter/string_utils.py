"""
String manipulation
"""
import logging
import re

LOGGER = logging.getLogger(__name__)


def replace(text: str, *pairs: str) -> str:
    """Do a series of global replacements on a string."""
    while pairs:
        text = pairs[1].join(text.split(pairs[0]))
        pairs = pairs[2:]
    return text


def cram(text: str, maximum_length: int) -> str:
    """Omit part of a string if needed to make it fit in a maximum length."""
    if len(text) > maximum_length:
        pre = max(0, (maximum_length - 3) // 2)
        post = max(0, maximum_length - 3 - pre)
        return text[:pre] + "..." + text[len(text) - post :]
    return text


_re_stripid = re.compile(r" at 0x[0-9a-f]{6,16}(>+)$", re.IGNORECASE)


def stripid(text: str) -> str:
    """Remove the hexadecimal id from a Python object representation."""
    # The behaviour of %p is implementation-dependent in terms of case.
    return _re_stripid.sub(r"\1", text)
