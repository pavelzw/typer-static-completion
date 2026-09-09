"""Ownership planning shared by sync and read-only checks."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .core import _output_path

MANIFEST = ".typer-static-completions.json"


@dataclass
class Plan:
    outputs: dict[Path, bytes]
    orphaned: tuple[Path, ...]
    conflicts: dict[Path, str]


def _digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _read_manifest(root: Path) -> dict[Path, dict[str, str]]:
    manifest = _output_path(root, MANIFEST)
    if not manifest.exists():
        return {}
    try:
        document = json.loads(manifest.read_bytes())
        if (
            not isinstance(document, dict)
            or document.get("version") != 1
            or not isinstance(document.get("files"), dict)
        ):
            raise ValueError("Expected version 1 ownership manifest")
        records: dict[Path, dict[str, str]] = {}
        for name, record in document["files"].items():
            path = _output_path(root, name)
            if path == manifest or manifest in path.parents:
                raise ValueError("Manifest cannot own itself")
            if not isinstance(record, dict) or set(record) != {"owner", "sha256"}:
                raise ValueError("Invalid ownership record")
            if not isinstance(record["owner"], str) or not record["owner"]:
                raise ValueError("Invalid owner")
            digest = record["sha256"]
            if (
                not isinstance(digest, str)
                or len(digest) != 64
                or any(char not in "0123456789abcdef" for char in digest)
            ):
                raise ValueError("Invalid content hash")
            if name != path.relative_to(root).as_posix():
                raise ValueError("Ownership paths must be canonical relative paths")
            if any(
                path == other or path in other.parents or other in path.parents
                for other in records
            ):
                raise ValueError("Colliding ownership paths")
            records[path] = record
        return records
    except (ValueError, UnicodeError, OSError) as exc:
        raise ValueError(
            f"Invalid completion ownership manifest {manifest}: {exc}"
        ) from exc


def prepare(
    root: Path,
    rendered: dict[Path, str],
    owners: dict[Path, str],
    skipped: dict[str, str],
    *,
    prune: bool,
    only_owners: frozenset[str] | None = None,
) -> Plan:
    manifest = _output_path(root, MANIFEST)
    previous = _read_manifest(root)
    outputs = {
        path: content.encode("utf-8") for path, content in sorted(rendered.items())
    }
    protected = set(skipped)
    if only_owners is not None:
        protected.update(
            record["owner"]
            for record in previous.values()
            if record["owner"] not in only_owners
        )
    records = dict(previous)
    conflicts: dict[Path, str] = {}
    orphaned: list[Path] = []
    for path, content in outputs.items():
        if path == manifest or manifest in path.parents or path in manifest.parents:
            raise ValueError(
                f"Completion layout collides with ownership manifest: {path}"
            )
        for old_path, record in previous.items():
            if path != old_path and (
                path in old_path.parents or old_path in path.parents
            ):
                raise ValueError(
                    f"Completion layout collides with previous ownership: {path}"
                )
            if path == old_path and record["owner"] in protected:
                conflicts[path] = (
                    "Destination belongs to an app that failed to import or is outside the selection"
                )
        if path not in previous and path.exists() and path.read_bytes() != content:
            conflicts[path] = "Unmanaged file has different content"
        records[path] = {"owner": owners[path], "sha256": _digest(content)}
    if prune:
        for path, record in previous.items():
            if path in outputs or record["owner"] in protected:
                continue
            if path.exists():
                if not path.is_file():
                    conflicts[path] = "Owned orphan is no longer a regular file"
                    continue
                orphaned.append(path)
                if _digest(path.read_bytes()) != record["sha256"]:
                    conflicts[path] = "Owned orphan was edited; refusing to delete it"
                    continue
            del records[path]
    document = {
        "version": 1,
        "files": {
            path.relative_to(root).as_posix(): record
            for path, record in sorted(records.items())
        },
    }
    outputs[manifest] = (
        json.dumps(document, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    # Preflight all files, including metadata, before sync mutates anything.
    for path in outputs:
        for parent in path.parents:
            if parent.exists() and not parent.is_dir():
                raise NotADirectoryError(parent)
        if path.exists() and not path.is_file():
            raise ValueError(f"Completion destination is not a regular file: {path}")
    return Plan(outputs, tuple(sorted(orphaned)), conflicts)
