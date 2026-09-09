"""Test extraction and generation behavior rather than scaffold API shape."""

import shlex
import shutil
import subprocess
from pathlib import Path

import pytest
import typer
from fixtures import fixture

from typer_static_completions import (
    Command,
    CommandTree,
    DynamicPolicy,
    GenerationOptions,
    IntrospectionError,
    Param,
    ParamKind,
    UnsupportedShellError,
    ValueKind,
    from_app,
    generate,
)
from typer_static_completions.verify import check_syntax


def candidates(script: str, line: str) -> list[str]:
    bash = shutil.which("bash")
    if not bash:
        pytest.skip("Bash is not installed")
    import re

    match = re.search(r"complete -F (\w+)", script)
    assert match is not None
    function = match[1]
    source = (
        script
        + f"COMP_LINE={shlex.quote(line)}; COMP_POINT=${{#COMP_LINE}}; {function}; printf '%s\\0' \"${{COMPREPLY[@]}}\""
    )
    result = subprocess.run(
        [bash, "--noprofile", "--norc"],
        input=source,
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    return result.stdout.rstrip("\0").split("\0") if result.stdout.rstrip("\0") else []


def test_extract_nested_tree():
    tree = from_app(fixture(), "demo")
    assert tree.paths() == (
        "deploy",
        "tasks",
        "tags",
        "remote",
        "remote add",
        "remote remove",
    )
    add = tree.find(["remote", "add"])
    assert add is not None
    assert add.arguments[0].flags == ()
    assert tree.find(["missing"]) is None
    deploy = tree.find(["deploy"])
    assert deploy is not None
    params = {p.name: p for p in deploy.options}
    assert params["cache"].flags == ("--cache", "--no-cache")
    assert not params["cache"].takes_value
    assert params["color"].choices == ("red", "rose", "blue", "two words", "quote's")
    assert params["directory"].value_kind is ValueKind.DIRECTORY
    assert params["config"].value_kind is ValueKind.FILE
    assert params["help"].is_help
    assert from_app(fixture(), "demo", max_depth=1).find(["remote", "add"]) is None


def test_leaf_hidden_and_custom_help():
    app = typer.Typer(
        add_completion=False, context_settings={"help_option_names": ["-h", "--assist"]}
    )

    @app.command()
    def main(secret: str = typer.Option("", hidden=True)):
        pass

    tree = from_app(app, "demo")
    assert not tree.root.is_group
    assert tree.root.options[0].flags == ("-h", "--assist") or tree.root.options[
        0
    ].flags == ("--assist", "-h")
    assert any(
        p.name == "secret"
        for p in from_app(app, "demo", include_hidden=True).root.options
    )
    assert "--assist" not in generate(
        app, "demo", options=GenerationOptions(include_help_option=False)
    )


@pytest.mark.parametrize(
    "line,expected",
    [
        ("demo dep", ["deploy"]),
        ("demo remote a", ["add"]),
        ("demo --profile remote dep", ["deploy"]),
        ('demo --profile "" dep', ["deploy"]),
        ("demo deploy --color bl", ["blue"]),
        ("demo deploy --color=bl", ["blue"]),
        ("demo deploy -cbl", ["-cblue"]),
        ("demo deploy --no-c", ["--no-cache"]),
        ("demo deploy --color red --c", ["--color", "--config", "--cache"]),
        ("demo deploy --color=red --c", ["--color", "--config", "--cache"]),
        ("demo deploy -cred --c", ["--color", "--config", "--cache"]),
        ("demo deploy -- --c", []),
        ("demo deploy --config remote a", []),
        ("demo deploy --unknown remote a", []),
        ("demo deploy --color two\\ w", ["two words"]),
    ],
)
def test_bash_candidates(line, expected):
    assert candidates(generate(fixture(), "demo"), line) == expected


def test_scalar_and_variadic_arguments():
    app = typer.Typer(add_completion=False)
    from fixtures import Color

    @app.command()
    def main(first: Color, rest: list[Color]):
        pass

    script = generate(app, "demo")
    assert candidates(script, "demo bl") == ["blue"]
    assert candidates(script, "demo blue red bl") == ["blue"]


def test_dynamic_policy():
    app = typer.Typer(add_completion=False)

    @app.command()
    def main(value: str = typer.Option("", autocompletion=lambda: ["secret"])):
        pass

    assert from_app(app, "demo").has_dynamic_params
    assert candidates(generate(app, "demo"), "demo --value ") == []
    for policy in (DynamicPolicy.ERROR, DynamicPolicy.DELEGATE):
        with pytest.raises(IntrospectionError, match="Dynamic callbacks"):
            generate(app, "demo", options=GenerationOptions(dynamic=policy))


def test_invalid_api_and_unsupported_shapes():
    with pytest.raises(ValueError, match="prog_name"):
        generate(fixture())
    with pytest.raises(ValueError, match="prog_name"):
        generate(CommandTree("demo", Command(())), "another")
    with pytest.raises(UnsupportedShellError):
        generate(fixture(), "demo", "powershell")
    with pytest.raises(IntrospectionError, match="[Cc]hain"):
        generate(CommandTree("demo", Command((), chain=True)))
    with pytest.raises(IntrospectionError, match="scalar"):
        generate(
            CommandTree(
                "demo",
                Command(
                    (),
                    params=(
                        Param(ParamKind.ARGUMENT, "pair", ValueKind.OPAQUE, nargs=2),
                    ),
                ),
            )
        )


def test_deterministic_literal_generation(tmp_path: Path):
    marker = tmp_path / "invoked"
    evil = f"$(touch {marker})"
    tree = CommandTree(
        "demo",
        Command(
            (),
            params=(
                Param(
                    ParamKind.OPTION,
                    "value",
                    ValueKind.CHOICE,
                    flags=("--value",),
                    choices=(evil, "quote's", "[bracket]:value", "two words"),
                ),
            ),
        ),
    )
    script = generate(tree)
    assert script == generate(tree)
    if not shutil.which("bash"):
        pytest.skip("Bash is not installed")
    check_syntax(script, "bash")
    assert candidates(script, "demo --value ") == [
        evil,
        "quote's",
        "[bracket]:value",
        "two words",
    ]
    assert not marker.exists()


def test_control_characters_rejected():
    with pytest.raises(IntrospectionError, match="control"):
        generate(CommandTree("bad\nname", Command(())))


def test_custom_generator_registration(monkeypatch):
    import typer_static_completions.generators as registry
    from typer_static_completions.generators.bash import BashGenerator

    monkeypatch.setattr(registry, "_REGISTRY", dict(registry._REGISTRY))

    class CustomGenerator(BashGenerator):
        shell = "custom"

    assert registry.register(CustomGenerator) is CustomGenerator
    assert "custom" in registry.available_shells()
    assert generate(fixture(), "demo", "custom") == generate(fixture(), "demo")
    with pytest.raises(ValueError, match="already registered"):
        registry.register(CustomGenerator)


def test_dynamic_omit_does_not_enable_file_fallback():
    tree = CommandTree(
        "demo",
        Command(
            (),
            params=(
                Param(
                    ParamKind.OPTION,
                    "value",
                    ValueKind.DYNAMIC,
                    flags=("--value",),
                ),
            ),
        ),
    )
    script = generate(tree, options=GenerationOptions(file_params=frozenset({"value"})))
    assert candidates(script, "demo --value ") == []


def test_invalid_shell_syntax():
    from typer_static_completions import ScriptSyntaxError

    if not shutil.which("bash"):
        pytest.skip("Bash is not installed")
    with pytest.raises(ScriptSyntaxError):
        check_syntax("broken() {", "bash")
