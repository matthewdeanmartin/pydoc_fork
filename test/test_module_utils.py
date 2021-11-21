import pydoc_fork.module_utils as module_utils

from types import ModuleType


def test_importfile():
    result = module_utils.importfile(__file__)
    assert isinstance(result, ModuleType)


# TODO: test a bad module
