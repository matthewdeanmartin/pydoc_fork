from types import ModuleType

import pydoc_fork.inspector.module_utils as module_utils


def test_importfile():
    result = module_utils.importfile(__file__)
    assert isinstance(result, ModuleType)


# TODO: test a bad module
