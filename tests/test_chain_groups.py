"""Reject chain settings before Typer drops them during conversion."""

import pytest
import typer
from typer.testing import CliRunner

from typer_static_completion import IntrospectionError, from_app, generate, write
from typer_static_completion.cli import main


def chain_app(**settings):
    app = typer.Typer(add_completion=False, **settings)

    @app.command()
    def build():
        typer.echo("built")

    @app.command()
    def publish():
        typer.echo("published")

    return app


def test_supported_typer_does_not_execute_chains():
    # Compatibility alarm: revisit our rejection if Typer restores chaining.
    result = CliRunner().invoke(chain_app(chain=True), ["build", "publish"])
    assert result.exit_code == 2
    assert "unexpected extra argument" in result.output.lower()
    assert "built" not in result.stdout


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_chain_generation_fails_explicitly(shell):
    with pytest.raises(IntrospectionError, match="chain=True.*Typer 0.26"):
        generate(chain_app(chain=True), "demo", shell)


def test_callback_chain_setting():
    app = chain_app()

    @app.callback(chain=True)
    def root():
        pytest.fail("Introspection invoked a callback")

    with pytest.raises(IntrospectionError, match="chain=True"):
        from_app(app, "demo")


@pytest.mark.parametrize("source", ["constructor", "registration"])
def test_nested_chain_setting(source):
    root = typer.Typer()
    child = chain_app(chain=True) if source == "constructor" else chain_app()
    if source == "registration":
        root.add_typer(child, name="pipeline", chain=True)
    else:
        root.add_typer(child, name="pipeline")
    with pytest.raises(IntrospectionError, match="chain=True"):
        from_app(root, "demo")


def test_explicit_false_overrides_constructor_and_callback():
    child = chain_app(chain=True)

    @child.callback(chain=True)
    def child_root():
        pytest.fail("Introspection invoked a callback")

    root = typer.Typer()
    root.add_typer(child, name="pipeline", chain=False)
    assert "pipeline" in generate(root, "demo")


def test_callback_false_overrides_constructor():
    app = chain_app(chain=True)

    @app.callback(chain=False)
    def root():
        pytest.fail("Introspection invoked a callback")

    assert "build" in generate(app, "demo")


def test_chain_failure_preserves_existing_output(tmp_path, monkeypatch, capsys):
    app = chain_app(chain=True)
    destination = tmp_path / "completion"
    destination.write_text("existing")
    monkeypatch.setattr("typer_static_completion.cli.load_app", lambda target: app)
    assert (
        main(
            [
                "generate",
                "fixture:app",
                "--prog-name",
                "demo",
                "--shell",
                "bash",
                "-o",
                str(destination),
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "chain=True" in captured.err and "Traceback" not in captured.err
    assert destination.read_text() == "existing"
    with pytest.raises(IntrospectionError, match="chain=True"):
        write(app, "demo", output_dir=tmp_path / "generated")
    assert not (tmp_path / "generated").exists()
