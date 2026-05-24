"""
Jinja setup
"""

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, PackageLoader, select_autoescape

from pydoc_fork import settings


def _build_loader():
    package_loader = PackageLoader("pydoc_fork")
    if settings.CUSTOM_TEMPLATES:
        return ChoiceLoader([FileSystemLoader(settings.CUSTOM_TEMPLATES), package_loader])
    return package_loader


JINJA_ENV = Environment(loader=_build_loader(), autoescape=select_autoescape())
"""Object to let Jinja find template folder"""
JINJA_ENV.globals.update(settings=settings)


def refresh_loader() -> None:
    """Rebuild the Jinja loader after settings change (e.g. CUSTOM_TEMPLATES set via config)."""
    JINJA_ENV.loader = _build_loader()
