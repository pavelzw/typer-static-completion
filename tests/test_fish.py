"""Native Fish regressions for literal command names and option dispatch."""

import shutil
import subprocess

import pytest
from fixtures import fixture

from typer_static_completions import (
    Command,
    CommandTree,
    Param,
    ParamKind,
    ValueKind,
    generate,
)
from typer_static_completions.generators.fish import FishGenerator


def complete(script, line):
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
    return [line.split("\t")[0] for line in result.stdout.splitlines()]


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
