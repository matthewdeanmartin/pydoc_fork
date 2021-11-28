"""
Jinja setup
"""
from jinja2 import Environment, PackageLoader, select_autoescape

JINJA_ENV = Environment(
    loader=PackageLoader("pydoc_fork"), autoescape=select_autoescape()
)
"""Object to let Jinja find template folder"""
