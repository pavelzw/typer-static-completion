"""Shared explicit-update policy for screen and generated-file snapshots."""

import os
from pathlib import Path

import pytest


def assert_snapshot(path: Path, actual: str) -> None:
    if os.environ.get("UPDATE_SNAPSHOTS") == "1":
        if os.environ.get("CI"):
            pytest.fail("Snapshot updates are disabled in CI")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(actual, encoding="utf-8")
    else:
        assert path.exists(), (
            f"Missing {path.name}; run pixi run -e snapshots update-snapshots and review"
        )
        assert actual == path.read_text(encoding="utf-8"), (
            "Review changes before running pixi run -e snapshots update-snapshots"
        )
