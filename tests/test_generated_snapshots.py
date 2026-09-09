"""Exact full completion scripts, independent of interactive dependencies."""

from pathlib import Path

import pytest
from fixtures import (
    case_fixture,
    coverage_fixture,
    fixture,
    group_argument_fixture,
    parsing_fixture,
    tuple_argument_fixture,
    tuple_fixture,
)
from snapshot_assertions import assert_snapshot

from typer_static_completions import generate
from typer_static_completions.cli import build_cli
from typer_static_completions.verify import check_syntax, is_available


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
@pytest.mark.parametrize(
    "name,make_app",
    [
        ("demo", fixture),
        ("parsing", parsing_fixture),
        ("cli", build_cli),
        ("coverage", coverage_fixture),
        ("tuple", tuple_fixture),
        ("case", case_fixture),
        ("tuple-arguments", tuple_argument_fixture),
        ("group-arguments", group_argument_fixture),
    ],
)
def test_generated_file(shell, name, make_app):
    program = "typer-static-completions" if name == "cli" else "demo"
    script = generate(make_app(), program, shell)
    assert script == generate(make_app(), program, shell)
    assert script.endswith("\n")
    if is_available(shell):
        check_syntax(script, shell)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "generated" / f"{name}.{shell}", script
    )
