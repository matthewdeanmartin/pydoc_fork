import sys
import os
from pydoc_fork.inspector.module_utils import safe_import

def test_safe_import_mocks_argv(tmp_path):
    """Test that safe_import mocks sys.argv during import."""
    module_dir = tmp_path / "mock_argv_module"
    module_dir.mkdir()
    (module_dir / "__init__.py").write_text("")
    main_py = module_dir / "__main__.py"
    main_py.write_text("import sys; ARGV_DURING_IMPORT = sys.argv")
    
    # Add tmp_path to sys.path so we can import our mock module
    sys.path.insert(0, str(tmp_path))
    try:
        # Before import, sys.argv is the original
        original_argv = sys.argv
        
        # Perform safe_import
        module = safe_import("mock_argv_module.__main__")
        
        # Check that ARGV_DURING_IMPORT was mocked
        assert hasattr(module, "ARGV_DURING_IMPORT")
        assert module.ARGV_DURING_IMPORT == ["mock_argv_module.__main__"]
        
        # Check that sys.argv was restored
        assert sys.argv == original_argv
    finally:
        sys.path.pop(0)

def test_safe_import_restores_argv_on_error(tmp_path):
    """Test that safe_import restores sys.argv even if an error occurs."""
    module_dir = tmp_path / "error_argv_module"
    module_dir.mkdir()
    (module_dir / "__init__.py").write_text("")
    main_py = module_dir / "__main__.py"
    main_py.write_text("import sys; raise RuntimeError('intentional error')")
    
    sys.path.insert(0, str(tmp_path))
    try:
        original_argv = sys.argv
        try:
            safe_import("error_argv_module.__main__")
        except Exception:
            pass
        
        # Check that sys.argv was restored even after error
        assert sys.argv == original_argv
    finally:
        sys.path.pop(0)
