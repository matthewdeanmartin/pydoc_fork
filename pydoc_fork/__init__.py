"""Generate Python documentation in HTML"""
# __all__ = ['help']
__author__ = "Ka-Ping Yee <ping@lfw.org>"
__date__ = "26 February 2001"

__credits__ = """Guido van Rossum, for an excellent programming language.
Tommy Burnette, the original creator of manpy.
Paul Prescod, for all his work on onlinehelp.
Richard Chamberlain, for the first implementation of textdoc.
"""

# Known bugs that can't be fixed here:
#   - synopsis() cannot be prevented from clobbering existing
#     loaded modules.
#   - If the __file__ attribute on a module is a relative path and
#     the current directory is changed with os.chdir(), an incorrect
#     path will be displayed.
from pydoc_fork.commands import *  # noqa

# from pydoc_fork.formatter_html import *  # noqa
# from pydoc_fork.module_utils import *  # noqa
# from pydoc_fork.path_utils import *  # noqa
# from pydoc_fork.string_utils import *  # noqa
# from pydoc_fork.utils import *  # noqa

# forgot why I needed this
# __spec__ = "123"  # noqa
