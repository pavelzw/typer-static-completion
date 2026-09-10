"""CLI streams, exit statuses, and project workflows."""

import pytest

from typer_static_completion.cli import main

TARGET = "typer_static_completion.cli:app"


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_generate_stdout(shell, capsys):
    assert main(["generate", TARGET, "--prog-name", "tsc", "--shell", shell]) == 0
    captured = capsys.readouterr()
    assert captured.out.endswith("\n")
    assert "tsc" in captured.out
    assert captured.err == ""


def test_generate_file_and_import_output(tmp_path, capsys, monkeypatch):
    from typer_static_completion.cli import app

    def noisy(target):
        print("module diagnostics")
        return app

    monkeypatch.setattr("typer_static_completion.cli.load_app", noisy)
    args = ["generate", TARGET, "--prog-name", "tsc", "--shell", "bash"]
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


@pytest.mark.parametrize(
    "args",
    [
        ["generate"],
        ["generate", TARGET, "--prog-name", "tsc", "--shell", "powershell"],
        [
            "generate",
            "_missing_cli_module:app",
            "--prog-name",
            "tsc",
            "--shell",
            "bash",
        ],
        ["sync"],
        ["check"],
        ["unknown-command"],
    ],
)
def test_errors_return_two_without_traceback(args, capsys):
    assert main(args) == 2
    assert "Traceback" not in capsys.readouterr().err


def test_help(capsys):
    assert main(["--help"]) == 0
    assert "generate" in capsys.readouterr().out


def test_generate_requires_shell_before_loading_app(capsys, monkeypatch):
    def unexpected_load(target):
        pytest.fail("App must not be loaded without a shell selection")

    monkeypatch.setattr("typer_static_completion.cli.load_app", unexpected_load)
    assert main(["generate", TARGET, "--prog-name", "tsc"]) == 2
    captured = capsys.readouterr()
    assert "--shell" in captured.err
    assert captured.out == ""
