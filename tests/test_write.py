"""Filesystem behavior for build-time completion generation."""

import os
from pathlib import Path

import pytest
from fixtures import fixture

from typer_static_completion import (
    GenerationOptions,
    UnsupportedShellError,
    from_app,
    generate,
    write,
)


def test_write_defaults_and_unchanged_mtimes(tmp_path):
    app = fixture()
    root = tmp_path / "completions"
    outputs = write(app, "demo", output_dir=root)
    assert set(outputs) == {
        root / "bash/demo",
        root / "zsh/_demo",
        root / "fish/demo.fish",
    }
    for path in outputs:
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))
    before = {path: path.stat().st_mtime_ns for path in outputs}
    assert write(app, "demo", output_dir=root) == outputs
    assert {path: path.stat().st_mtime_ns for path in outputs} == before
    for path, content in outputs.items():
        assert path.read_bytes() == content.encode("utf-8")
        assert content == generate(app, "demo", path.parent.name)
    changed = write(
        app, "demo", output_dir=root, options=GenerationOptions(banner=False)
    )
    assert changed != outputs
    assert all(
        path.read_bytes() == content.encode("utf-8")
        for path, content in changed.items()
    )


def test_dry_run_tree_layout_and_shell_iterator(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    tree = from_app(fixture(), "demo")
    outputs = write(
        tree,
        shells=iter(["fish", "fish"]),
        dry_run=True,
        output_dir="preview",
        layout={"fish": "vendor/{prog}.fish"},
    )
    assert outputs == {Path("preview/vendor/demo.fish"): generate(tree, shell="fish")}
    assert not Path("preview").exists()
    assert (
        write(
            tree,
            shells=["fish"],
            output_dir="preview",
            layout={"fish": "vendor/{prog}.fish"},
        )
        == outputs
    )
    assert write(tree, shells=[], output_dir="empty") == {}
    assert not Path("empty").exists()


@pytest.mark.parametrize(
    "layout",
    [
        {"bash": "../escape"},
        {"bash": "."},
        {"bash": "same", "fish": "same"},
        {"bash": "same", "fish": "same/child"},
    ],
)
def test_invalid_layout_does_not_write(tmp_path, layout):
    root = tmp_path / "output"
    with pytest.raises(ValueError):
        write(
            fixture(), "demo", shells=["bash", "fish"], output_dir=root, layout=layout
        )
    assert not root.exists()


def test_absolute_layout_and_unsafe_program_name(tmp_path):
    with pytest.raises(ValueError):
        write(
            fixture(),
            "demo",
            output_dir=tmp_path / "output",
            layout={"bash": str(tmp_path / "escape")},
        )
    with pytest.raises(ValueError):
        write(fixture(), "../../escape", output_dir=tmp_path / "output")
    assert not (tmp_path / "output").exists()


def test_generation_failure_keeps_existing_files(tmp_path):
    outputs = write(fixture(), "demo", output_dir=tmp_path)
    before = {path: path.read_bytes() for path in outputs}
    with pytest.raises(UnsupportedShellError):
        write(
            fixture(),
            "demo",
            output_dir=tmp_path,
            shells=["bash", "powershell"],
            options=GenerationOptions(banner=False),
        )
    assert {path: path.read_bytes() for path in outputs} == before


def test_destination_failure_does_not_update_earlier_files(tmp_path):
    outputs = write(fixture(), "demo", output_dir=tmp_path, shells=["bash"])
    (tmp_path / "fish").write_text("handwritten")
    with pytest.raises(NotADirectoryError):
        write(
            fixture(),
            "demo",
            output_dir=tmp_path,
            shells=["bash", "fish"],
            options=GenerationOptions(banner=False),
        )
    assert all(path.read_text() == content for path, content in outputs.items())


def test_symlink_destination_is_rejected(tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    root = tmp_path / "output"
    root.mkdir()
    try:
        (root / "bash").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlinks unavailable")
    with pytest.raises(ValueError):
        write(fixture(), "demo", output_dir=root)
    assert list(outside.iterdir()) == []


def test_failed_replace_cleans_temporary_file(tmp_path, monkeypatch):
    outputs = write(fixture(), "demo", output_dir=tmp_path, shells=["bash"])

    def fail_replace(source, destination):
        raise OSError("injected failure")

    monkeypatch.setattr(os, "replace", fail_replace)
    with pytest.raises(OSError, match="injected failure"):
        write(
            fixture(),
            "demo",
            output_dir=tmp_path,
            shells=["bash"],
            options=GenerationOptions(banner=False),
        )
    assert set((tmp_path / "bash").iterdir()) == set(outputs)
    assert all(path.read_text() == content for path, content in outputs.items())


def test_replacement_preserves_permissions(tmp_path):
    if os.name == "nt":
        pytest.skip("POSIX file permissions")
    outputs = write(fixture(), "demo", output_dir=tmp_path, shells=["bash"])
    path = next(iter(outputs))
    path.chmod(0o640)
    write(
        fixture(),
        "demo",
        output_dir=tmp_path,
        shells=["bash"],
        options=GenerationOptions(banner=False),
    )
    assert path.stat().st_mode & 0o777 == 0o640


def test_dry_run_existing_files_stay_unchanged(tmp_path):
    outputs = write(fixture(), "demo", output_dir=tmp_path)
    preview = write(
        fixture(),
        "demo",
        output_dir=tmp_path,
        dry_run=True,
        options=GenerationOptions(banner=False),
    )
    assert preview != outputs
    assert all(
        path.read_bytes() == content.encode("utf-8")
        for path, content in outputs.items()
    )
