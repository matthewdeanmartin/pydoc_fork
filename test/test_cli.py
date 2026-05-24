import sys

import pydoc_fork.cli as cli


def test_main_dispatches_to_gui(monkeypatch):
    called = []

    monkeypatch.setattr(sys, "argv", ["pydoc", "gui"])
    monkeypatch.setattr("pydoc_fork.gui.main", lambda: called.append("gui"))

    assert cli.main() == 0
    assert called == ["gui"]


def test_main_dispatches_to_html_generator(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["pydoc", "collections"])
    monkeypatch.setattr("pydoc_fork.__main__.main", lambda: 17)

    assert cli.main() == 17
