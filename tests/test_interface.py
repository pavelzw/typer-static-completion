"""Contract tests for the public interface.

The implementation is still stubs, so these assert the *shape* of the API: that
the exports exist, that the model is usable without typer, and that the typer
internals :mod:`typer_static_completions.introspect` relies on are present in the
installed typer. That last group is the valuable one -- it is what will fail
loudly when a typer upgrade moves something, instead of silently generating a
broken script.
"""

import inspect
from dataclasses import FrozenInstanceError

import pytest

import typer_static_completions as tsc


def test_public_exports_exist():
    missing = [name for name in tsc.__all__ if not hasattr(tsc, name)]
    assert missing == []


def test_errors_share_a_base():
    for exc in (
        tsc.UnsupportedShellError,
        tsc.AppLoadError,
        tsc.IntrospectionError,
        tsc.StaleCompletionsError,
        tsc.ShellUnavailableError,
        tsc.ScriptSyntaxError,
    ):
        assert issubclass(exc, tsc.StaticCompletionError)


def test_shell_members_are_strings():
    assert tsc.Shell.fish == "fish"
    assert set(tsc.DEFAULT_SHELLS) == {tsc.Shell.bash, tsc.Shell.zsh, tsc.Shell.fish}
    # PowerShell has a generator but is opt-in: it needs a $PROFILE edit rather
    # than a directory the shell scans.
    assert tsc.Shell.powershell not in tsc.DEFAULT_SHELLS


def test_model_is_constructible_without_typer():
    """Generators must be testable against hand-built trees."""
    param = tsc.Param(
        kind=tsc.ParamKind.OPTION,
        name="color",
        value_kind=tsc.ValueKind.CHOICE,
        flags=("--color",),
        choices=("red", "blue"),
    )
    tree = tsc.CommandTree(
        prog_name="demo",
        root=tsc.Command(
            path=(),
            subcommands={"hello": tsc.Command(path=("hello",), params=(param,))},
        ),
    )
    assert tree.prog_name == "demo"
    assert tree.root.subcommands["hello"].params[0].choices == ("red", "blue")


def test_model_is_frozen():
    cmd = tsc.Command(path=())
    with pytest.raises(FrozenInstanceError):
        cmd.help = "nope"  # type: ignore[misc]  # Deliberately test frozen assignment.


def test_generation_options_are_value_comparable():
    """--check must be able to prove it regenerated under the same settings."""
    assert tsc.GenerationOptions() == tsc.GenerationOptions()
    assert tsc.GenerationOptions(include_help=False) != tsc.GenerationOptions()


def test_dynamic_policy_defaults_to_hybrid():
    assert tsc.GenerationOptions().dynamic is tsc.DynamicPolicy.DELEGATE


@pytest.mark.parametrize(
    "shell,filename",
    [("bash", "{prog}"), ("zsh", "_{prog}"), ("fish", "{prog}.fish")],
)
def test_generator_filenames(shell, filename):
    """zsh requires the leading underscore; the others must not have one."""
    from typer_static_completions.generators import bash, fish, zsh

    generators = {
        "bash": bash.BashGenerator,
        "zsh": zsh.ZshGenerator,
        "fish": fish.FishGenerator,
    }
    assert generators[shell].filename == filename


def test_every_public_callable_is_documented():
    for name in tsc.__all__:
        obj = getattr(tsc, name)
        if inspect.isfunction(obj) or inspect.isclass(obj):
            assert obj.__doc__, f"{name} has no docstring"


class TestTyperInternals:
    """Pin the private typer attributes that introspection depends on.

    These are the four traps documented in ``introspect``; each one silently
    produces a plausible-but-wrong script if typer moves it.
    """

    def test_vendored_click_is_not_upstream_click(self):
        """Why shtab cannot be reused here."""
        typer_click = pytest.importorskip("typer._click.core")
        click = pytest.importorskip("click")
        assert typer_click.Command is not click.Command

    def test_choice_lives_in_typer_types(self):
        from typer._types import TyperChoice

        assert hasattr(TyperChoice("ab"), "choices")

    def test_arguments_carry_opts_too(self):
        """The trap behind the bogus ``-s ame`` flag."""
        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def cmd(name: str, loud: bool = False): ...

        params = {p.name: p for p in get_command(app).params}
        assert params["name"].param_type_name == "argument"
        # Non-empty opts on a positional: filtering on truthiness of opts breaks.
        assert params["name"].opts
        assert params["loud"].param_type_name == "option"

    def test_bool_option_negation_lives_in_secondary_opts(self):
        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def cmd(loud: bool = typer.Option(False, "--loud/--no-loud")): ...

        loud = {p.name: p for p in get_command(app).params}["loud"]
        assert loud.opts == ["--loud"]
        assert loud.secondary_opts == ["--no-loud"]

    def test_path_and_file_types_are_named_not_isinstance_checked(self):
        from pathlib import Path

        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def cmd(
            config: Path = typer.Option(None),
            stream: typer.FileText = typer.Option(None),
        ): ...

        params = {p.name: p for p in get_command(app).params}
        assert params["config"].type.name == "path"
        assert params["stream"].type.name == "filename"

    def test_help_option_is_not_in_params(self):
        """Why ``--help`` must be read from the app, not hardcoded."""
        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def cmd(): ...

        command = get_command(app)
        assert "--help" not in [o for p in command.params for o in p.opts]
        assert command.add_help_option is True

    def test_single_command_app_collapses_to_a_leaf(self):
        """A one-command app has no group, so the root is a leaf."""
        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def only(): ...

        assert not getattr(get_command(app), "commands", {})

    def test_custom_autocompletion_is_recorded_for_detection(self):
        """How DynamicPolicy detects a parameter it cannot bake in."""
        import typer
        from typer.main import get_command

        app = typer.Typer()

        @app.command()
        def cmd(name: str = typer.Option("", autocompletion=lambda: ["a", "b"])): ...

        name = {p.name: p for p in get_command(app).params}["name"]
        assert getattr(name, "_custom_shell_complete", None) is not None
