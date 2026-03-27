"""
Jinja setup
"""

from jinja2 import Environment, PackageLoader, select_autoescape

from pydoc_fork import settings

JINJA_ENV = Environment(
    loader=PackageLoader("pydoc_fork"), autoescape=select_autoescape()
)
JINJA_ENV.globals.update(settings=settings)
"""Object to let Jinja find template folder"""
