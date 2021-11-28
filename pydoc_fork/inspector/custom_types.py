"""
Custom Types so mypy can check the code
"""
from typing import List

from typing_extensions import Protocol


# noinspection SpellCheckingInspection
class TypeLike(Protocol):
    """This is a union of all sort of types"""

    __name__: str
    __module__: str
    __path__: str
    # noinspection SpellCheckingInspection
    __objclass__: "TypeLike"
    __func__: "TypeLike"
    __self__: "TypeLike"
    __bases__: List["TypeLike"]
    __all__: List[str]
    __qualname__: str
    __file__: str
    __mro__: str

    # pure metadata, people can write about anything here
    __version__: str
    __date__: str
    __author__: str
    __credits__: str
