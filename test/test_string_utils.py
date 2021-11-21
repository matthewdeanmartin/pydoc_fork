import pydoc_fork.string_utils as string_utils


def test_replace():
    result = string_utils.replace("abc xyz", "xyz", "abc")
    assert result == "abc abc"
    result = string_utils.replace("abc xyz pdq", "xyz", "abc", "pdq", "abc")
    assert result == "abc abc abc"
    result = string_utils.replace(
        "abc xyz pdq", "abc", "111", "xyz", "222", "pdq", "333"
    )
    assert result == "111 222 333"


def test_cram_basic():
    assert string_utils.cram("1234567890", 7) == "12...90"
    assert string_utils.cram("1234567890", 6) == "1...90"
    assert string_utils.cram("1234567890", 5) == "1...0"


def test_cram_degenerate():
    assert string_utils.cram("1234567890", 4) == "...0"
    assert string_utils.cram("1234567890", 3) == "..."
    assert string_utils.cram("1234567890", 2) == "..."
    assert string_utils.cram("1234567890", 1) == "..."
    assert string_utils.cram("1234567890", 0) == "..."


def test_stripid():
    # it is looking for the "> at hex" pattern
    assert string_utils.stripid("<function <lambda>") == "<function <lambda>"
    assert (
        string_utils.stripid("<function <lambda> at 0x00000288C38C9160>")
        == "<function <lambda>>"
    )
    assert string_utils.stripid(" at 0x00000288C38C9160>") == ">"
    assert string_utils.stripid("<a>>") == "<a>>"
    # this is not robust to a lot of scenarios
