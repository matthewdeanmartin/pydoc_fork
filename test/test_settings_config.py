import textwrap

from pydoc_fork import settings


def test_parse_toml_reads_current_directory_config(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool.pydoc_fork]
            PREFER_DOCS_PYTHON_ORG = true
            "ONLY-NAMED-AND-SUBS" = true
            "PROJECT-NAME" = "Sample Docs"
            """),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    parsed = settings.parse_toml(None)

    assert parsed["PREFER_DOCS_PYTHON_ORG"] is True
    assert parsed["ONLY_NAMED_AND_SUBS"] is True
    assert parsed["PROJECT_NAME"] == "Sample Docs"


def test_load_config_reads_supported_values(tmp_path, monkeypatch):
    (tmp_path / "pyproject.toml").write_text(
        textwrap.dedent("""
            [tool.pydoc_fork]
            PREFER_DOCS_PYTHON_ORG = true
            DOCUMENT_INTERNALS = false
            SKIP_MODULES = ["typing", "pathlib"]
            "ONLY-NAMED-AND-SUBS" = true
            THEME = "dark"
            "CUSTOM-TEMPLATES" = "custom_templates"
            GENERATE_INDEX = false
            "PROJECT-NAME" = "Configured Project"
            """),
        encoding="utf-8",
    )
    monkeypatch.setattr(settings, "PREFER_DOCS_PYTHON_ORG", False)
    monkeypatch.setattr(settings, "DOCUMENT_INTERNALS", True)
    monkeypatch.setattr(settings, "SKIP_MODULES", ["typing"])
    monkeypatch.setattr(settings, "ONLY_NAMED_AND_SUBS", False)
    monkeypatch.setattr(settings, "THEME", "classic")
    monkeypatch.setattr(settings, "CUSTOM_TEMPLATES", None)
    monkeypatch.setattr(settings, "GENERATE_INDEX", True)
    monkeypatch.setattr(settings, "PROJECT_NAME", "Python Project")

    settings.load_config(str(tmp_path))

    assert settings.PREFER_DOCS_PYTHON_ORG is True
    assert settings.DOCUMENT_INTERNALS is False
    assert settings.SKIP_MODULES == ["typing", "pathlib"]
    assert settings.ONLY_NAMED_AND_SUBS is True
    assert settings.THEME == "dark"
    assert settings.CUSTOM_TEMPLATES == "custom_templates"
    assert settings.GENERATE_INDEX is False
    assert settings.PROJECT_NAME == "Configured Project"


def test_load_config_uses_defaults_when_pyproject_is_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "PREFER_DOCS_PYTHON_ORG", True)
    monkeypatch.setattr(settings, "DOCUMENT_INTERNALS", False)
    monkeypatch.setattr(settings, "SKIP_MODULES", ["custom"])
    monkeypatch.setattr(settings, "ONLY_NAMED_AND_SUBS", True)
    monkeypatch.setattr(settings, "THEME", "dark")
    monkeypatch.setattr(settings, "CUSTOM_TEMPLATES", "custom_templates")
    monkeypatch.setattr(settings, "GENERATE_INDEX", False)
    monkeypatch.setattr(settings, "PROJECT_NAME", "Configured Project")

    settings.load_config(str(tmp_path))

    assert settings.PREFER_DOCS_PYTHON_ORG is False
    assert settings.DOCUMENT_INTERNALS is True
    assert settings.SKIP_MODULES == ["typing"]
    assert settings.ONLY_NAMED_AND_SUBS is False
    assert settings.THEME == "classic"
    assert settings.CUSTOM_TEMPLATES is None
    assert settings.GENERATE_INDEX is True
    assert settings.PROJECT_NAME == "Python Project"
