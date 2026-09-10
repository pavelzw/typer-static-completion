"""Readline replacement boundaries follow the user's COMP_WORDBREAKS."""

import json
import shlex
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from fixtures import word_break_fixture
from snapshot_assertions import assert_snapshot
from snapshot_harness import capture_state
from typer.testing import CliRunner

from typer_static_completions import generate

SETTINGS = [
    ("default", None),
    ("no-delimiters", " \t\n"),
    ("colon", " \t\n:"),
    ("equals", " \t\n="),
    ("at", " \t\n@"),
    ("all", " \t\n:=@"),
]
CASES = [
    ("colon", "demo --value svc:p", "svc:prod"),
    ("address", "demo --value user@ex", "user@example.org"),
    ("equals", "demo --value key=va", "key=value"),
    ("assigned-colon", "demo --value=svc:p", "svc:prod"),
    ("assigned-address", "demo --value=user@ex", "user@example.org"),
    ("assigned-equals", "demo --value=key=va", "key=value"),
    ("quoted-address", "demo --value 'user@ex", "user@example.org"),
    ("escaped-address", r"demo --value user\@ex", "user@example.org"),
    ("quoted-colon", "demo --value 'svc:p", "svc:prod"),
    ("quoted-assignment", 'demo --value="key=va', "key=value"),
    ("escaped-colon", r"demo --value svc\:p", "svc:prod"),
    ("attached-address", "demo -vuser@ex", "user@example.org"),
]


@pytest.mark.parametrize("name,line,value", CASES, ids=[c[0] for c in CASES])
def test_word_break_screen(name, line, value):
    sections = []
    for setting, breaks in SETTINGS:
        script = generate(word_break_fixture(), "demo", "bash")
        if breaks is not None:
            script += "COMP_WORDBREAKS=" + shlex.quote(breaks) + "\n"
        result = capture_state(script, line + "<TAB>", shell="bash")
        assert result.line is not None
        assert result.cursor == len(result.line), result
        assert result.screen == "> " + result.line + "▏\n", result
        words = shlex.split(result.line)[1:]
        if line.startswith("demo --value="):
            assert words == ["--value=" + value]
        elif line.startswith("demo -v"):
            assert words == ["-v" + value]
        else:
            assert words == ["--value", value]
        parsed = CliRunner().invoke(word_break_fixture(), words)
        assert parsed.exit_code == 0, parsed.output
        assert parsed.stdout == value + "\n"
        sections.append(
            f"Setting: {setting}\nCOMP_WORDBREAKS: {json.dumps(breaks)}\n\n{result.screen}\nBuffer: {json.dumps(result.line)}\nCursor: {result.cursor}\n"
        )
    actual = f"Input: {line}<TAB>\nShell: bash\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "word-breaks" / f"{name}.snap", actual
    )
