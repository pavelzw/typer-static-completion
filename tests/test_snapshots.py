"""Reviewed interactive screens: local updates are explicit and forbidden in CI."""

import os
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from fixtures import fixture
from snapshot_assertions import assert_snapshot
from snapshot_harness import capture

from typer_static_completions import generate

CASES = {
    "subcommand": "demo dep<TAB>",
    "ambiguous-subcommands": "demo ta<TAB><TAB>",
    "no-match": "demo zzz<TAB>",
    "nested-command": "demo remote a<TAB>",
    "choice": "demo deploy --color bl<TAB>",
    "ambiguous-choice": "demo deploy --color r<TAB><TAB>",
    "assignment": "demo deploy --color=bl<TAB>",
    "short-attached": "demo deploy -cbl<TAB>",
    "negation": "demo deploy --no-c<TAB>",
    "space-choice": "demo deploy --color two<TAB>",
    "empty-option-value": 'demo --profile "" dep<TAB>',
    "apostrophe-choice": "demo deploy --color quote<TAB>",
    "apostrophe-file": "demo deploy --config quote<TAB>",
    "attached-file": "demo deploy --config=two<TAB>",
    "file": "demo deploy --config two<TAB>",
    "quoted-file": 'demo deploy --config "two<TAB>',
    "quoted-choice": 'demo deploy --color "two<TAB>',
    "escaped-choice": "demo deploy --color two\\ w<TAB>",
    "directory": "demo deploy --directory nest<TAB>",
    "cursor-middle": "demo deploy --color bl --no-cache<LEFT:11><TAB>",
    "option-value-is-command": "demo --profile remote dep<TAB>",
}


@pytest.mark.parametrize("name,input", CASES.items())
def test_screen(name, input):
    if os.environ.get("UPDATE_SNAPSHOTS") == "1" and os.environ.get("CI"):
        pytest.fail("Snapshot updates are disabled in CI")
    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(generate(fixture(), "demo", shell), input, shell=shell)
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(Path(__file__).with_name("snapshots") / f"{name}.snap", actual)
