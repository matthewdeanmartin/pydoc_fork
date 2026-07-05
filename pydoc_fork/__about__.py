"""Metadata for pydoc_fork."""

__all__ = [
    "__credits__",
    "__dependencies__",
    "__description__",
    "__keywords__",
    "__license__",
    "__readme__",
    "__requires_python__",
    "__status__",
    "__title__",
    "__version__",
]

__title__ = "pydoc_fork"
__version__ = "3.4.0"
__description__ = "Fork of cpython's pydoc module to do just html document generation"
__readme__ = "README.md"
__credits__ = [{"name": "Matthew Martin", "email": "matthewdeanmartin@gmail.com"}]
__keywords__ = ["pydoc", "html documentation"]
__license__ = "MIT"
__requires_python__ = ">=3.10"
__status__ = "4 - Beta"
__dependencies__ = [
    "docopt-ng>=0.9.0,<1",
    "jinja2>=3.1.4,<4",
    "markdown>=3.5.2,<4",
    "docutils==0.20.1",
    "tomli>=2.0.1,<3",
    "typing_extensions",
]
