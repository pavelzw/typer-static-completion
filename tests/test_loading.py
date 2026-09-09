"""Loading imports apps without invoking CLI wrappers or factories."""

import sys
from types import ModuleType, SimpleNamespace

import pytest
from fixtures import fixture

from typer_static_completions import AppLoadError, CompletionSet
from typer_static_completions.introspect import load_app


def test_load_explicit_nested_and_bare_targets(monkeypatch, tmp_path):
    app = fixture()
    module = ModuleType("_completion_test_app")
    module.__dict__["app"] = app
    module.__dict__["nested"] = SimpleNamespace(cli=app)
    monkeypatch.setitem(sys.modules, module.__name__, module)
    assert load_app(module.__name__) is app
    assert load_app(module.__name__ + ":nested.cli") is app
    completions = CompletionSet({"demo": module.__name__ + ":app"}, output_dir=tmp_path)
    completions.sync()
    assert completions.check()


def test_wrappers_are_never_called(monkeypatch):
    called = []

    def main():
        called.append(True)
        return fixture()

    module = ModuleType("_completion_test_wrapper")
    module.__dict__["main"] = main
    monkeypatch.setitem(sys.modules, module.__name__, module)
    with pytest.raises(AppLoadError, match="not called"):
        load_app(module.__name__ + ":main")
    assert not called


def test_import_system_exit_is_reported(monkeypatch):
    def exit_import(name):
        raise SystemExit(2)

    monkeypatch.setattr("importlib.import_module", exit_import)
    with pytest.raises(AppLoadError, match="Cannot load"):
        load_app("broken:app")
