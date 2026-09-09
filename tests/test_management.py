"""Set-level generation, ownership, and failure recovery."""

import json
import os
from pathlib import Path

import pytest
from fixtures import fixture

from typer_static_completions import (
    AppLoadError,
    CheckResult,
    CompletionSet,
    GenerationOptions,
    StaleCompletionsError,
    from_app,
    write,
)
from typer_static_completions._management import MANIFEST


def manager(root, names=("alpha", "beta"), **kwargs):
    return CompletionSet(
        {name: fixture() for name in names},
        output_dir=root,
        shells=["bash", "fish", "zsh"],
        **kwargs,
    )


def files(root):
    return {
        path.relative_to(root): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_sync_check_render_and_stability(tmp_path):
    root = tmp_path / "output"
    completions = manager(root)
    expected = completions.render()
    assert len(expected) == 6
    assert set(completions.trees()) == {"alpha", "beta"}
    initial = completions.check()
    assert not initial
    assert set(initial.missing) == {*expected, root / MANIFEST}
    assert not root.exists()
    result = completions.sync()
    assert set(result.written) == {*expected, root / MANIFEST}
    assert not result.skipped
    assert "7 written" in result.report()
    assert completions.check().ok
    completions.check().raise_for_status()
    for path in result.written:
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    before = {path: path.stat().st_mtime_ns for path in result.written}
    repeat = completions.sync()
    assert not repeat.written
    assert set(repeat.unchanged) == set(result.written)
    assert {path: path.stat().st_mtime_ns for path in result.written} == before
    assert files(root) == {
        path.relative_to(root): content.encode() for path, content in expected.items()
    } | {Path(MANIFEST): (root / MANIFEST).read_bytes()}
    reverse = manager(root, names=("beta", "alpha"))
    assert reverse.check().ok


def test_stale_missing_diffs_and_no_writes(tmp_path):
    completions = manager(tmp_path)
    completions.sync()
    stale = tmp_path / "bash/alpha"
    missing = tmp_path / "fish/beta.fish"
    stale.write_bytes(b"# old completion\n")
    missing.unlink()
    before = files(tmp_path)
    result = completions.check()
    assert result.stale == (stale,)
    assert result.missing == (missing,)
    assert "-# old completion" in result.diffs[stale]
    assert " (generated)" in result.diffs[stale]
    assert result.diffs == completions.check().diffs
    assert not completions.check(diffs=False).diffs
    assert files(tmp_path) == before
    with pytest.raises(StaleCompletionsError, match="1 stale, 1 missing"):
        result.raise_for_status()
    completions.sync()
    assert completions.check()


def test_rename_prunes_only_owned_files_in_custom_layout(tmp_path):
    layout = {shell: f"vendor/{shell}/{{prog}}" for shell in ("bash", "fish", "zsh")}
    manager(tmp_path, names=("old",), layout=layout).sync()
    handwritten = tmp_path / "vendor/bash/handwritten"
    handwritten.write_text("keep this")
    renamed = manager(tmp_path, names=("new",), layout=layout)
    assert set(renamed.check().orphaned) == {
        tmp_path / f"vendor/{shell}/old" for shell in layout
    }
    result = renamed.sync()
    assert len(result.removed) == 3
    assert handwritten.read_text() == "keep this"
    assert renamed.check()


def test_no_prune_retains_ownership_for_later(tmp_path):
    manager(tmp_path).sync()
    single = manager(tmp_path, names=("alpha",))
    assert single.check(prune=False)
    single.sync(prune=False)
    assert (tmp_path / "bash/beta").exists()
    assert len(single.check().orphaned) == 3
    single.sync()
    assert not (tmp_path / "bash/beta").exists()
    assert single.check()


def test_failed_import_retains_outputs_and_makes_check_fail(tmp_path):
    manager(tmp_path).sync()
    beta = {
        path: path.read_bytes()
        for path in (
            tmp_path / "bash/beta",
            tmp_path / "fish/beta.fish",
            tmp_path / "zsh/_beta",
        )
    }
    broken = CompletionSet(
        {"alpha": fixture(), "beta": "_missing_completion_test_module:app"},
        output_dir=tmp_path,
        options=GenerationOptions(banner=False),
    )
    check = broken.check()
    assert not check
    assert set(check.skipped) == {"beta"}
    assert not check.orphaned
    result = broken.sync()
    assert set(result.skipped) == {"beta"}
    assert all(path.read_bytes() == content for path, content in beta.items())
    assert not result.removed
    assert not broken.check()
    assert "beta" in broken.check().report()
    with pytest.raises(AppLoadError):
        broken.render()
    with pytest.raises(AppLoadError):
        broken.trees()
    # Ownership remains usable after the import is fixed or the app is removed.
    assert len(manager(tmp_path, names=("alpha",)).sync().removed) == 3


def test_unmanaged_destination_conflict_and_matching_adoption(tmp_path):
    manager(tmp_path, names=("alpha",)).sync()
    handwritten = tmp_path / "bash/beta"
    handwritten.write_text("handwritten")
    completions = manager(tmp_path)
    before = files(tmp_path)
    assert handwritten in completions.check().conflicts
    with pytest.raises(ValueError, match="Unmanaged"):
        completions.sync()
    assert files(tmp_path) == before
    handwritten.unlink()
    write(fixture(), "beta", output_dir=tmp_path)
    completions.sync()
    assert completions.check()


def test_edited_orphan_is_not_deleted(tmp_path):
    manager(tmp_path).sync()
    edited = tmp_path / "bash/beta"
    edited.write_text("handwritten replacement")
    remaining = manager(tmp_path, names=("alpha",))
    before = files(tmp_path)
    assert edited in remaining.check().conflicts
    with pytest.raises(ValueError, match="edited"):
        remaining.sync()
    assert files(tmp_path) == before
    remaining.sync(prune=False)
    assert edited.exists()


@pytest.mark.parametrize(
    "layout",
    [
        {"bash": "same"},
        {"bash": MANIFEST},
        {"bash": MANIFEST + "/child"},
        {"fish": "../escape"},
    ],
)
def test_invalid_set_layout_never_writes(tmp_path, layout):
    root = tmp_path / "output"
    with pytest.raises(ValueError):
        manager(root, layout=layout).sync()
    assert not root.exists()


def test_invalid_manifest_never_writes(tmp_path):
    manager(tmp_path).sync()
    manifest = tmp_path / MANIFEST
    for data in [
        "broken",
        json.dumps({"version": 99, "files": {}}),
        json.dumps(
            {"version": 1, "files": {"../escape": {"owner": "old", "sha256": "0" * 64}}}
        ),
    ]:
        manifest.write_text(data)
        before = files(tmp_path)
        with pytest.raises(ValueError, match="manifest"):
            manager(tmp_path).sync()
        assert files(tmp_path) == before


def test_owned_symlink_cannot_be_pruned(tmp_path):
    root = tmp_path / "output"
    manager(root).sync()
    outside = tmp_path / "outside"
    outside.write_text("keep")
    old = root / "bash/beta"
    old.unlink()
    try:
        old.symlink_to(outside)
    except OSError:
        pytest.skip("Symlinks unavailable")
    with pytest.raises(ValueError):
        manager(root, names=("alpha",)).sync()
    assert outside.read_text() == "keep"


def test_failed_replacement_leaves_recoverable_ownership(tmp_path, monkeypatch):
    import typer_static_completions.core as core

    manager(tmp_path).sync()
    before = (tmp_path / MANIFEST).read_bytes()
    actual = core._replace_file
    count = 0

    def fail_second(path, data):
        nonlocal count
        count += 1
        if count == 2:
            raise OSError("injected")
        actual(path, data)

    monkeypatch.setattr(core, "_replace_file", fail_second)
    changed = manager(tmp_path, options=GenerationOptions(banner=False))
    with pytest.raises(OSError, match="injected"):
        changed.sync()
    assert (tmp_path / MANIFEST).read_bytes() == before
    monkeypatch.setattr(core, "_replace_file", actual)
    changed.sync()
    assert changed.check()


def test_empty_set_prunes_owned_outputs(tmp_path):
    manager(tmp_path).sync()
    empty = manager(tmp_path, names=())
    result = empty.sync()
    assert len(result.removed) == 6
    assert empty.check()
    assert set(files(tmp_path)) == {Path(MANIFEST)}


def test_tree_name_and_shell_iterable(tmp_path):
    tree = from_app(fixture(), "alpha")
    with pytest.raises(ValueError, match="mapping key"):
        CompletionSet({"beta": tree}, output_dir=tmp_path)
    completions = CompletionSet(
        {"alpha": tree}, output_dir=tmp_path, shells=iter(["fish", "fish"])
    )
    completions.sync()
    assert completions.check()
    assert set(completions.render()) == {tmp_path / "fish/alpha.fish"}


def test_reports_are_bounded():
    paths = tuple(Path(str(i)) for i in range(10))
    result = CheckResult(
        stale=paths, diffs={path: "a" * 2000 + "\n" + "line\n" * 100 for path in paths}
    )
    report = result.report(max_files=1)
    assert "9 more entries" in report
    assert "diff truncated" in report
    assert len(report) < 2000
    assert "diff truncated" not in result.report(show_diffs=False)
    with pytest.raises(ValueError):
        result.report(max_files=-1)
    assert CheckResult().report() == "Completions are up to date."


def test_failed_app_cannot_lose_path_to_another_app(tmp_path):
    layout = {"bash": "shared"}
    CompletionSet(
        {"old": fixture()}, output_dir=tmp_path, shells=["bash"], layout=layout
    ).sync()
    changed = CompletionSet(
        {"old": "_missing_completion_test_module:app", "new": fixture()},
        output_dir=tmp_path,
        shells=["bash"],
        layout=layout,
    )
    before = files(tmp_path)
    assert tmp_path / "shared" in changed.check().conflicts
    with pytest.raises(ValueError, match="failed to import"):
        changed.sync()
    assert files(tmp_path) == before


def test_generation_error_aborts_entire_set(tmp_path):
    from typer_static_completions import Command, CommandTree, IntrospectionError

    manager(tmp_path).sync()
    before = files(tmp_path)
    broken = CompletionSet(
        {"alpha": fixture(), "beta": CommandTree("beta", Command((), chain=True))},
        output_dir=tmp_path,
        options=GenerationOptions(banner=False),
    )
    with pytest.raises(IntrospectionError):
        broken.sync()
    assert files(tmp_path) == before


def test_failed_pruning_keeps_manifest_for_retry(tmp_path, monkeypatch):
    manager(tmp_path).sync()
    manifest = tmp_path / MANIFEST
    before = manifest.read_bytes()
    original = Path.unlink

    def fail_beta(path, *args, **kwargs):
        if path == tmp_path / "fish/beta.fish":
            raise OSError("injected deletion failure")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", fail_beta)
    remaining = manager(tmp_path, names=("alpha",))
    with pytest.raises(OSError, match="deletion failure"):
        remaining.sync()
    assert manifest.read_bytes() == before
    monkeypatch.setattr(Path, "unlink", original)
    remaining.sync()
    assert remaining.check()


def test_diff_marks_missing_final_newline(tmp_path):
    completions = manager(tmp_path, names=("alpha",))
    completions.sync()
    path = tmp_path / "bash/alpha"
    path.write_bytes(path.read_bytes().rstrip(b"\n"))
    diff = completions.check().diffs[path]
    assert "\n\\ No newline at end of file\n+" in diff
