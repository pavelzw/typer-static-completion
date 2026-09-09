"""CLI streams, exit statuses, and project workflows."""

import pytest

from typer_static_completions.cli import main

TARGET = "typer_static_completions.cli:app"


def project(tmp_path):
    path = tmp_path / "pyproject.toml"
    path.write_text('[project.scripts]\ntsc = "typer_static_completions.cli:main"\n')
    return ["--pyproject", str(path), "--app", "tsc=" + TARGET]


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_generate_stdout(shell, capsys):
    assert main(["generate", TARGET, "--prog-name", "tsc", "--shell", shell]) == 0
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")
    assert "tsc" in captured.out
    assert captured.err == ""


def test_generate_file_and_import_output(tmp_path, capsys, monkeypatch):
    from typer_static_completions.cli import app

    def noisy(target):
        print("module diagnostics")
        return app

    monkeypatch.setattr("typer_static_completions.cli.load_app", noisy)
    args = ["generate", TARGET, "--prog-name", "tsc"]
    assert main(args) == 0
    captured = capsys.readouterr()
    assert captured.err == "module diagnostics\n"
    assert "module diagnostics" not in captured.out
    path = tmp_path / "sub/completion"
    assert main([*args, "-o", str(path)]) == 0
    assert path.read_text() == captured.out
    before = path.stat().st_mtime_ns
    assert main([*args, "-o", str(path)]) == 0
    assert path.stat().st_mtime_ns == before


def test_sync_check_workflow(tmp_path, capsys):
    args = project(tmp_path)
    root = tmp_path / "completions"
    assert main(["check", *args]) == 1
    assert not root.exists()
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "missing" in captured.err
    assert main(["sync", *args]) == 0
    assert "written" in capsys.readouterr().out
    assert main(["check", *args]) == 0
    assert "up to date" in capsys.readouterr().err
    file = root / "bash/tsc"
    file.write_text("old\n")
    assert main(["check", *args, "--no-diff", "--max-files", "1"]) == 1
    assert "-old" not in capsys.readouterr().err
    assert file.read_text() == "old\n"
    assert main(["check", *args]) == 1
    assert "-old" in capsys.readouterr().err


def test_nearest_project_shell_selection_and_relative_output(tmp_path, monkeypatch):
    project(tmp_path)
    nested = tmp_path / "nested"
    nested.mkdir()
    monkeypatch.chdir(nested)
    args = ["--app", "tsc=" + TARGET, "--shell", "fish", "--shell", "zsh"]
    assert main(["sync", *args]) == 0
    assert (tmp_path / "completions/fish/tsc.fish").exists()
    assert not (tmp_path / "completions/bash").exists()
    assert main(["sync", *args, "--output-dir", "custom"]) == 0
    assert (nested / "custom/zsh/_tsc").exists()


@pytest.mark.parametrize(
    "args",
    [
        ["generate"],
        ["generate", TARGET, "--prog-name", "tsc", "--shell", "powershell"],
        ["generate", "_missing_cli_module:app", "--prog-name", "tsc"],
        ["check", "--max-files", "-1"],
        ["unknown-command"],
    ],
)
def test_errors_return_two_without_traceback(args, capsys):
    assert main(args) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_partial_sync_and_invalid_overrides(tmp_path, capsys):
    args = project(tmp_path)
    assert main(["sync", "--pyproject", args[1]]) == 1
    assert "skipped" in capsys.readouterr().out
    assert main(["sync", *args, "--app", "bad-format"]) == 2
    assert main(["sync", *args, "--app", "tsc=" + TARGET]) == 2
    assert main(["sync", "--pyproject", str(tmp_path / "missing.toml")]) == 2


def test_help(capsys):
    assert main(["--help"]) == 0
    assert "generate" in capsys.readouterr().out
