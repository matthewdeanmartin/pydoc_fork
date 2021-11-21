import pydoc_fork.formatter_html as doc
import pydoc_fork.format_page as page
import pydoc_fork.module_utils as module_utils
from pydoc_fork.path_utils import locate_file


def test_HTMLDoc_index():
    # one directory, needs to be a subdirectory of working folder, or full path
    directory = "module_examples"
    # the shadowed module name will not have a hyperlink & will be grey/disabled
    shadowed = {
        "pydoc_mod": 0,
    }
    result = page.index(directory, shadowed)
    assert directory in result
    # with open("doc_index.html", "w", encoding="utf-8") as output:
    #     output.write(result)


def test_HTMLDoc_document_module():
    file_name = locate_file("pydocfodder.py", __file__)
    module = module_utils.importfile(file_name)
    name = "The NAME"
    result = page.document(module, name)

    # this is surprising.
    assert name not in result

    with open("just_module.html", "w", encoding="utf-8") as output:
        output.write(result)


def test_HTMLDoc_document_class():
    class Stuff:
        pass

    name = "The HTML doc Class"
    result = page.document(Stuff, name)
    assert name in result
    with open("just_class.html", "w", encoding="utf-8") as output:
        output.write(result)


def test_HTMLDoc_document_routine():

    name = "The Routine"

    def waka():
        """Does this show??"""
        return "wa wa"

    result = page.document(waka, name)
    assert name in result

    # well this is surprising.
    assert "Does this show??" not in result
    with open("just_routine.html", "w", encoding="utf-8") as output:
        output.write(result)


def test_HTMLDoc_document_other():

    name = "The Number"
    result = page.document(42, name)
    assert name in result
    with open("just_other.html", "w", encoding="utf-8") as output:
        output.write(result)
