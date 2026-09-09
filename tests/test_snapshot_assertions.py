"""Snapshot checks never create or overwrite baselines implicitly."""

import pytest
from snapshot_assertions import assert_snapshot


def test_missing_snapshot_is_not_created(tmp_path, monkeypatch):
    monkeypatch.delenv("UPDATE_SNAPSHOTS", raising=False)
    path = tmp_path / "missing.snap"
    with pytest.raises(AssertionError, match="Missing"):
        assert_snapshot(path, "new")
    assert not path.exists()


def test_ci_cannot_update_snapshot(tmp_path, monkeypatch):
    path = tmp_path / "existing.snap"
    path.write_text("old")
    monkeypatch.setenv("CI", "1")
    monkeypatch.setenv("UPDATE_SNAPSHOTS", "1")
    with pytest.raises(pytest.fail.Exception, match="disabled in CI"):
        assert_snapshot(path, "new")
    assert path.read_text() == "old"
