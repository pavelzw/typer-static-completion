"""Pyproject discovery and selective management without invoking wrappers."""

import sys
from types import ModuleType

import pytest
from fixtures import fixture

from typer_static_completions import AppLoadError, CompletionSet, from_app
from typer_static_completions.introspect import entrypoints


def project(
    path, text='[project.scripts]\nalpha = "example:main"\nbeta = "example:app"\n'
):
    path.write_text(text, encoding="utf-8")
    return path


def test_nearest_project_is_authoritative(tmp_path, monkeypatch):
    outer = project(tmp_path / "pyproject.toml")
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)
    assert entrypoints() == {"alpha": "example:main", "beta": "example:app"}
    project(nested / "pyproject.toml", '[project]\nname = "nested"\n')
    with pytest.raises(AppLoadError, match="project.scripts"):
        entrypoints()
    assert entrypoints(str(outer))["alpha"] == "example:main"


@pytest.mark.parametrize(
    "text",
    [
        "not valid TOML [",
        "[project]\n",
        "[project]\nscripts = []\n",
        "[project.scripts]\na = 123\n",
        '[project.scripts]\n"" = "example:app"\n',
        '[project.scripts]\na = "example"\n',
        '[project.scripts]\na = "example:app()"\n',
        '[project.scripts]\na = "example::app"\n',
    ],
)
def test_invalid_metadata_is_reported(tmp_path, text):
    path = project(tmp_path / "pyproject.toml", text)
    with pytest.raises(AppLoadError, match="pyproject.toml"):
        entrypoints(path)


def test_missing_unreadable_and_empty_projects(tmp_path, monkeypatch):
    with pytest.raises(AppLoadError):
        entrypoints(tmp_path / "missing.toml")
    with pytest.raises(AppLoadError):
        entrypoints(tmp_path)
    assert (
        entrypoints(project(tmp_path / "pyproject.toml", "[project.scripts]\n")) == {}
    )
    monkeypatch.setattr("pathlib.Path.exists", lambda self: False)
    with pytest.raises(AppLoadError, match="No pyproject.toml"):
        entrypoints()


def test_discovery_is_lazy_and_overrides_wrappers(tmp_path, monkeypatch):
    module = ModuleType("_discovery_fixture")
    called = []

    def main():
        called.append(True)
        raise AssertionError("wrapper invoked")

    module.__dict__.update(main=main, app=fixture())
    monkeypatch.setitem(sys.modules, module.__name__, module)
    path = project(
        tmp_path / "pyproject.toml",
        '[project.scripts]\nalpha = "_discovery_fixture:main"\nbeta = "_discovery_fixture:app"\n',
    )
    root = tmp_path / "output"
    unresolved = CompletionSet.from_pyproject(path, output_dir=root)
    assert not root.exists()
    assert "alpha" in unresolved.check().skipped
    for override in (fixture(), from_app(fixture(), "alpha"), "_discovery_fixture:app"):
        completions = CompletionSet.from_pyproject(
            path, output_dir=root, overrides={"alpha": override}
        )
        completions.sync()
        assert completions.check()
    assert not called


def test_discovery_does_not_import_or_change_paths(tmp_path, monkeypatch):
    path = project(tmp_path / "pyproject.toml")
    before = list(sys.path)

    def fail_import(*args):
        raise AssertionError("import during discovery")

    # Warm the TOML reader before blocking imports.
    entrypoints(path)
    monkeypatch.setattr("importlib.import_module", fail_import)
    completions = CompletionSet.from_pyproject(path, output_dir="relative")
    assert set(completions.apps) == {"alpha", "beta"}
    assert str(completions.output_dir) == "relative"
    assert sys.path == before


@pytest.mark.parametrize(
    "kwargs", [{"only": ["typo"]}, {"overrides": {"typo": "example:app"}}]
)
def test_unknown_names_are_rejected(tmp_path, kwargs):
    path = project(tmp_path / "pyproject.toml")
    with pytest.raises(AppLoadError, match="typo"):
        CompletionSet.from_pyproject(path, output_dir=tmp_path / "output", **kwargs)
    assert not (tmp_path / "output").exists()


def test_selection_preserves_excluded_and_removed_owners(tmp_path):
    path = project(tmp_path / "pyproject.toml")
    root = tmp_path / "output"
    overrides = {"alpha": fixture(), "beta": fixture()}
    CompletionSet.from_pyproject(path, output_dir=root, overrides=overrides).sync()
    beta = root / "bash/beta"
    original = beta.read_bytes()
    selected = CompletionSet.from_pyproject(
        path,
        output_dir=root,
        only=["alpha", "alpha"],
        overrides={"alpha": fixture(), "beta": "_missing_module:app"},
    )
    assert selected.check()
    selected.sync()
    assert beta.read_bytes() == original
    # Removed names are also outside an explicit selection, until a full sync.
    project(path, '[project.scripts]\nalpha = "example:app"\n')
    CompletionSet.from_pyproject(
        path, output_dir=root, only=["alpha"], overrides={"alpha": fixture()}
    ).sync()
    assert beta.read_bytes() == original
    empty = CompletionSet.from_pyproject(path, output_dir=root, only=[])
    assert empty.check()
    assert not empty.sync().removed
    all_apps = CompletionSet.from_pyproject(
        path, output_dir=root, overrides={"alpha": fixture()}
    )
    assert len(all_apps.sync().removed) == 3
    assert not beta.exists()


def test_selection_cannot_take_excluded_destination(tmp_path):
    path = project(tmp_path / "pyproject.toml")
    root = tmp_path / "output"
    CompletionSet(
        {"beta": fixture()}, output_dir=root, shells=["bash"], layout={"bash": "shared"}
    ).sync()
    selected = CompletionSet.from_pyproject(
        path,
        output_dir=root,
        only=["alpha"],
        overrides={"alpha": fixture()},
        shells=["bash"],
        layout={"bash": "shared"},
    )
    before = (root / "shared").read_bytes()
    with pytest.raises(ValueError, match="outside the selection"):
        selected.sync()
    assert (root / "shared").read_bytes() == before
