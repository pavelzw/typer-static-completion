"""Exact full completion scripts, independent of interactive dependencies."""

from pathlib import Path

import pytest
from fixtures import fixture, parsing_fixture
from snapshot_assertions import assert_snapshot

from typer_static_completions import generate
from typer_static_completions.verify import check_syntax, is_available


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
@pytest.mark.parametrize(
    "name,make_app", [("demo", fixture), ("parsing", parsing_fixture)]
)
def test_generated_file(shell, name, make_app):
    script = generate(make_app(), "demo", shell)
    assert script == generate(make_app(), "demo", shell)
    assert script.endswith("\n")
    if is_available(shell):
        check_syntax(script, shell)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "generated" / f"{name}.{shell}", script
    )
