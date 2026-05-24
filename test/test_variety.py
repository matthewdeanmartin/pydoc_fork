import os
import sys

import pytest

from pydoc_fork import process_path_or_dot_name


@pytest.fixture
def sample_codebase(tmp_path):
    """Creates a variety of Python files to document."""
    base = tmp_path / "sample_project"
    base.mkdir()

    # 1. Simple module
    mod1 = base / "simple_mod.py"
    mod1.write_text('"""A simple module."""\ndef func1(x):\n    """Function 1."""\n    return x\n', encoding="utf-8")

    # 2. Class with various members
    mod2 = base / "class_mod.py"
    mod2.write_text(
        '"""Module with a class."""\n'
        "class MyClass:\n"
        '    """A sample class."""\n'
        "    def __init__(self, value):\n"
        '        """Init."""\n'
        "        self.value = value\n"
        "\n"
        "    def method(self):\n"
        '        """A method."""\n'
        "        return self.value\n"
        "\n"
        "    @classmethod\n"
        "    def cm(cls):\n"
        '        """Class method."""\n'
        "        pass\n"
        "\n"
        "    @staticmethod\n"
        "    def sm():\n"
        '        """Static method."""\n'
        "        pass\n",
        encoding="utf-8",
    )

    # 3. Package
    pkg = base / "my_package"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('"""My package."""', encoding="utf-8")
    (pkg / "sub_mod.py").write_text('"""Sub module."""\ndef sub_func(): pass', encoding="utf-8")

    # 4. Nested package
    subpkg = pkg / "sub_package"
    subpkg.mkdir()
    (subpkg / "__init__.py").write_text('"""Nested package."""', encoding="utf-8")

    # 5. Module with __all__
    mod_all = base / "all_mod.py"
    mod_all.write_text(
        '''"""Module with __all__."""
__all__ = ["public_func"]
def public_func():
    """Public."""
    pass
def private_func():
    """Private."""
    pass
''',
        encoding="utf-8",
    )

    # 6. Inheritance
    mod_inh = base / "inheritance_mod.py"
    mod_inh.write_text(
        '''"""Module with inheritance."""
class BaseClass:
    """Base class."""
    def base_method(self):
        """Method in base."""
        pass
    def override_method(self):
        """Method to be overridden."""
        pass

class DerivedClass(BaseClass):
    """Derived class."""
    def override_method(self):
        """Overridden method."""
        pass
    def derived_method(self):
        """Method in derived."""
        pass
''',
        encoding="utf-8",
    )

    # 7. Properties and Data
    mod_prop = base / "property_mod.py"
    mod_prop.write_text(
        '"""Module with properties."""\n'
        "MY_CONSTANT = 42\n"
        '"""A constant."""\n'
        "\n"
        "class PropClass:\n"
        '    """Class with property."""\n'
        "    def __init__(self):\n"
        "        self._x = 0\n"
        "\n"
        "    @property\n"
        "    def x(self):\n"
        '        """Property x."""\n'
        "        return self._x\n"
        "\n"
        "    @x.setter\n"
        "    def x(self, value):\n"
        "        self._x = value\n",
        encoding="utf-8",
    )

    # 8. Private members
    mod_priv = base / "private_mod.py"
    mod_priv.write_text(
        '''"""Module with private members."""
def _private_func():
    """Private function."""
    pass

class _PrivateClass:
    """Private class."""
    def public_method(self):
        pass

def public_func():
    """Public function."""
    pass
''',
        encoding="utf-8",
    )

    return base


def test_document_simple_module(sample_codebase, tmp_path):
    """Test documenting a simple module."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["simple_mod"], output_folder=str(output))

        html_file = output / "simple_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        # pydoc_fork might escape space to &nbsp;
        assert "A simple module." in content.replace("&nbsp;", " ")
        assert "func1" in content
        assert "Function 1." in content.replace("&nbsp;", " ")
    finally:
        sys.path.pop(0)


def test_document_class_module(sample_codebase, tmp_path):
    """Test documenting a module with a class."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["class_mod"], output_folder=str(output))

        html_file = output / "class_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "MyClass" in content
        assert "A sample class." in content.replace("&nbsp;", " ")
        assert "method" in content
        assert "cm" in content
        assert "sm" in content
    finally:
        sys.path.pop(0)


def test_document_package(sample_codebase, tmp_path):
    """Test documenting a package."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["my_package"], output_folder=str(output))

        # pydoc_fork might name it my_package.html or my_package.__init__.html
        html_file = output / "my_package.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "My package." in content.replace("&nbsp;", " ")

        # Check if submodules are mentioned/documented
        assert "sub_mod" in content
        assert "sub_package" in content
    finally:
        sys.path.pop(0)


def test_document_module_with_all(sample_codebase, tmp_path):
    """Test documenting a module with __all__."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["all_mod"], output_folder=str(output))

        html_file = output / "all_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "public_func" in content
    finally:
        sys.path.pop(0)


def test_document_inheritance(sample_codebase, tmp_path):
    """Test documenting inheritance."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["inheritance_mod"], output_folder=str(output))

        html_file = output / "inheritance_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "BaseClass" in content
        assert "DerivedClass" in content
        assert "base_method" in content
        assert "override_method" in content
        assert "derived_method" in content
        # It should show that DerivedClass inherits from BaseClass
        assert "BaseClass" in content  # This might be a link or text
    finally:
        sys.path.pop(0)


def test_document_properties(sample_codebase, tmp_path):
    """Test documenting properties and constants."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        process_path_or_dot_name(["property_mod"], output_folder=str(output))

        html_file = output / "property_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "MY_CONSTANT" in content
        assert "PropClass" in content
        assert "Property x." in content.replace("&nbsp;", " ")
    finally:
        sys.path.pop(0)


def test_document_private(sample_codebase, tmp_path):
    """Test documenting private members."""
    output = tmp_path / "output"
    output.mkdir()

    sys.path.insert(0, str(sample_codebase))
    try:
        # Default behavior might exclude private members unless specified
        process_path_or_dot_name(["private_mod"], output_folder=str(output))

        html_file = output / "private_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "public_func" in content
        # _private_func should NOT be in the default documentation
        # unless document_internals=True (which is not default)
        assert "_private_func" not in content
        assert "_PrivateClass" not in content
    finally:
        sys.path.pop(0)


def test_document_by_relative_path(sample_codebase, tmp_path):
    """Test documenting by providing a relative file path."""
    output = tmp_path / "output"
    output.mkdir()

    old_cwd = os.getcwd()
    os.chdir(str(sample_codebase))
    try:
        # pydoc often handles 'mod.py'
        process_path_or_dot_name(["simple_mod.py"], output_folder=str(output))

        html_file = output / "simple_mod.html"
        assert html_file.exists()
        content = html_file.read_text(encoding="utf-8")
        assert "A simple module." in content.replace("&nbsp;", " ")
    finally:
        os.chdir(old_cwd)
