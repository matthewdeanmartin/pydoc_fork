from typing import Iterable, List

from typing_extensions import Protocol


class TypeLike(Protocol):
    __name__: str
    __module__: str
    __date__: str
    __author__: str
    __credits__: str
    __path__: str
    __objclass__: str
    # def __name__(self) -> str:
    #    ...  # Empty method body (explicit '...')


class ClassLike(Protocol):
    __self__: str
    __name__: str
    __bases__: List[str]


class ModuleLike(Protocol):
    __name__: str
    __version__: str
    __qualname__: str
    __doc__: str
    __file__: str
