"""This is a test module for test_pydoc"""

__author__ = "Benjamin Peterson"
__credits__ = "Nobody"
__version__ = "1.2.3.4"
__xyz__ = "X, Y and Z"


class A:
    """Hello and goodbye"""

    def __init__():  # pylint: disable=no-method-argument
        """Wow, I have no function!"""
        pass  # pylint: disable=unnecessary-pass


class B:
    NO_MEANING: str = "eggs"
    pass  # pylint: disable=unnecessary-pass


class C:
    def say_no(self):
        return "no"

    def get_answer(self):
        """Return say_no()"""
        return self.say_no()

    def is_it_true(self):
        """Return self.get_answer()"""
        return self.get_answer()


def doc_func():
    """
    This function solves all of the world's problems:
    hunger
    lack of Python
    war
    """


def nodoc_func():
    pass
