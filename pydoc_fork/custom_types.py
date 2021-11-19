"""
Custom Types so mypy can check the code
"""
from typing import List

from typing_extensions import Protocol


class TypeLike(Protocol):
    """This is a union of all sort of types"""

    __name__: str
    __module__: str
    __date__: str
    __author__: str
    __credits__: str
    __path__: str
    __objclass__: "TypeLike"
    __func__: "TypeLike"
    __self__: "TypeLike"
    __bases__: List["TypeLike"]
    __version__: str
    __all__: List[str]
    __qualname__: str
    __file__: str
    __mro__: str
    # def __name__(self) -> str:
    #    ...  # Empty method body (explicit '...')
