"""Native Fish regressions for literal command names and option dispatch."""

import shutil
import subprocess

import pytest
from fixtures import fixture

from typer_static_completions import (
    Command,
    CommandTree,
    GenerationOptions,
    Param,
    ParamKind,
    ValueKind,
    generate,
)
from typer_static_completions.generators.fish import FishGenerator


def complete(script, line, *, descriptions=False):
    executable = shutil.which("fish")
    if not executable:
        pytest.skip("Fish is not installed")
    source = script + "\ncomplete -C " + FishGenerator().quote(line)
    result = subprocess.run(
        [executable, "--no-config", "-c", source],
        text=True,
        capture_output=True,
        timeout=5,
        check=True,
    )
    lines = result.stdout.splitlines()
    return lines if descriptions else [line.split("\t")[0] for line in lines]


def test_command_names_are_literal():
    child = Command(
        ("foo*",),
        params=(Param(ParamKind.OPTION, "flag", ValueKind.FLAG, flags=("--flag",)),),
    )
    tree = CommandTree("demo", Command((), subcommands={"foo*": child}))
    script = generate(tree, shell="fish")
    assert complete(script, "demo 'foo*' --f") == ["--flag"]
    assert complete(script, "demo foobar --f") == []


@pytest.mark.parametrize(
    "line,expected",
    [
        ("demo --profile remote dep", ["deploy"]),
        ("demo deploy --color=bl", ["--color=blue"]),
        ("demo deploy -cbl", ["-cblue"]),
        ("demo deploy -- --no-c", []),
    ],
)
def test_native_candidates(line, expected):
    assert complete(generate(fixture(), "demo", "fish"), line) == expected


@pytest.mark.parametrize("include_help", [True, False])
def test_value_descriptions(include_help):
    tree = CommandTree(
        "demo",
        Command(
            (),
            params=(
                Param(
                    ParamKind.OPTION,
                    "color",
                    ValueKind.CHOICE,
                    flags=("--color",),
                    choices=("red",),
                    help="Choose a color",
                ),
            ),
        ),
    )
    script = generate(
        tree, shell="fish", options=GenerationOptions(include_help=include_help)
    )
    expected = "red\tChoose a color" if include_help else "red"
    assert complete(script, "demo --color r", descriptions=True) == [expected]
