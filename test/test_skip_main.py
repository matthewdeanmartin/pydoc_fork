import os
import shutil
from pydoc_fork.commands import document_directory

def test_document_directory_skips_main(tmp_path):
    """Test that document_directory skips __main__ modules."""
    module_dir = tmp_path / "test_pkg"
    module_dir.mkdir()
    (module_dir / "__init__.py").write_text("")
    (module_dir / "useful.py").write_text("def foo(): pass")
    (module_dir / "__main__.py").write_text("import sys; raise SystemExit(1)")
    
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    
    # Add tmp_path to sys.path so we can import our mock module
    import sys
    sys.path.insert(0, str(tmp_path))
    try:
        # Run document_directory on the test package
        written = document_directory(str(tmp_path), str(output_dir), for_only="test_pkg")
        
        # Verify that useful.py was documented but __main__.py was not
        written_basenames = [os.path.basename(p) for p in written]
        assert "test_pkg.useful.html" in written_basenames
        assert "test_pkg.__main__.html" not in written_basenames
        assert "test_pkg.html" in written_basenames
    finally:
        sys.path.pop(0)
