"""
Custom Types so mypy can check the code
"""

from typing import Any, Union

from typing_extensions import Protocol


# noinspection SpellCheckingInspection
class TypeLike(Protocol):
    """This is a union of all sort of types"""

    __name__: str
    __module__: str
    __doc__: str | None
    __path__: Union[str, list[str]] | None
    # noinspection SpellCheckingInspection
    __objclass__: Any | None
    __func__: Any | None
    __self__: Any | None
    __bases__: list[Any] | None
    __all__: list[str] | None
    __qualname__: str | None
    __file__: str | None
    __mro__: Any | None

    # pure metadata, people can write about anything here
    __version__: str | None
    __date__: str | None
    __author__: str | None
    __credits__: str | None
