"""Exact full completion scripts, independent of interactive dependencies."""

from pathlib import Path

import pytest
from fixtures import fixture
from snapshot_assertions import assert_snapshot

from typer_static_completions import generate
from typer_static_completions.verify import check_syntax, is_available


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_generated_file(shell):
    script = generate(fixture(), "demo", shell)
    assert script == generate(fixture(), "demo", shell)
    assert script.endswith("\n")
    if is_available(shell):
        check_syntax(script, shell)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "generated" / f"demo.{shell}", script
    )
