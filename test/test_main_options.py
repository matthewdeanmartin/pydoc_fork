import logging
from unittest.mock import patch

import pydoc_fork.__main__ as main_module
from pydoc_fork import settings


def test_process_docopts_applies_optional_cli_settings(tmp_path, monkeypatch):
    arguments = {
        "<config>": str(tmp_path),
        "<package>": ["example_pkg"],
        "--output": str(tmp_path / "docs"),
        "--document_internals": True,
        "--prefer_docs_python_org": True,
        "--theme": "dark",
        "--project_name": "Example Project",
        "--no_index": True,
        "--quiet": False,
        "--verbose": True,
    }
    loaded = []
    processed = []
    original_loggers = {
        name: (logging.getLogger(name).level, list(logging.getLogger(name).handlers))
        for name in ("pydoc_fork", "__main__")
    }

    monkeypatch.setattr(main_module, "LOGGERS", [])
    monkeypatch.setattr(main_module, "load_config", loaded.append)
    monkeypatch.setattr(
        main_module.commands,
        "process_path_or_dot_name",
        lambda package, output_folder: processed.append((package, output_folder)),
    )
    monkeypatch.setattr(settings, "DOCUMENT_INTERNALS", False)
    monkeypatch.setattr(settings, "PREFER_DOCS_PYTHON_ORG", False)
    monkeypatch.setattr(settings, "THEME", "classic")
    monkeypatch.setattr(settings, "PROJECT_NAME", "Python Project")
    monkeypatch.setattr(settings, "GENERATE_INDEX", True)

    try:
        with patch("docopt.docopt", return_value=arguments):
            assert main_module.main() == 0
    finally:
        for name, (level, handlers) in original_loggers.items():
            logger = logging.getLogger(name)
            for handler in list(logger.handlers):
                if handler not in handlers:
                    logger.removeHandler(handler)
                    handler.close()
            logger.setLevel(level)

    assert loaded == [str(tmp_path)]
    assert processed == [(["example_pkg"], str(tmp_path / "docs"))]
    assert settings.DOCUMENT_INTERNALS is True
    assert settings.PREFER_DOCS_PYTHON_ORG is True
    assert settings.THEME == "dark"
    assert settings.PROJECT_NAME == "Example Project"
    assert settings.GENERATE_INDEX is False
    assert [logger.name for logger in main_module.LOGGERS] == ["pydoc_fork", "__main__"]
