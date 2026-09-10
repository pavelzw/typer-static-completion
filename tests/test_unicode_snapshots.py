"""Check Unicode editing state independently of the rendered terminal screen."""

import json
import shlex
import unicodedata
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from fixtures import unicode_fixture
from snapshot_assertions import assert_snapshot
from snapshot_harness import capture_state
from typer.testing import CliRunner

from typer_static_completion import generate

CASES = [
    ("cjk-insert", "demo --value 東<TAB>", "demo --value 東京 ▏"),
    ("cjk-complete", "demo --value 東京<TAB>", "demo --value 東京 ▏"),
    ("emoji-insert", "demo --value 🚀l<TAB>", "demo --value 🚀launch ▏"),
    ("combining-insert", "demo --value cafe<TAB>", "demo --value cafe\u0301 ▏"),
    ("combining-prefix", "demo --value cafe\u0301<TAB>", "demo --value cafe\u0301 ▏"),
    (
        "multiple-combining",
        "demo --value a\u0308\u0301v<TAB>",
        "demo --value a\u0308\u0301value ▏",
    ),
    ("cjk-assigned", "demo --value=東<TAB>", "demo --value=東京 ▏"),
    ("emoji-attached", "demo -v🚀l<TAB>", "demo -v🚀launch ▏"),
    (
        "cjk-middle",
        "demo --value 東 --quiet<LEFT:8><TAB>",
        "demo --value 東京 ▏--quiet",
    ),
    (
        "emoji-middle",
        "demo --value 🚀l --quiet<LEFT:8><TAB>",
        "demo --value 🚀launch ▏--quiet",
    ),
    (
        "combining-middle",
        "demo --value cafe\u0301 --quiet<LEFT:8><TAB>",
        "demo --value cafe\u0301 ▏--quiet",
    ),
    ("cjk-before-cursor", "demo --value 東京 --qu<TAB>", "demo --value 東京 --quiet ▏"),
    (
        "emoji-before-cursor",
        "demo --value 🚀launch --qu<TAB>",
        "demo --value 🚀launch --quiet ▏",
    ),
    (
        "combining-before-cursor",
        "demo --value cafe\u0301 --qu<TAB>",
        "demo --value cafe\u0301 --quiet ▏",
    ),
]


@pytest.mark.parametrize("name,input,expected", CASES)
def test_unicode_screen(name, input, expected):
    sections = []
    for shell in ("bash", "fish", "zsh"):
        result = capture_state(
            generate(unicode_fixture(), "demo", shell),
            input,
            shell=shell,
            locale="C.UTF-8",
        )
        native_expected = expected
        # Preserve native cursor placement when completing before another word.
        if shell == "bash":
            native_expected = expected.replace(" ▏--quiet", "▏ --quiet")
        elif shell == "zsh":
            native_expected = expected.replace(" ▏--quiet", " ▏ --quiet")
        assert result.line == native_expected.replace("▏", ""), (shell, result)
        assert result.cursor == native_expected.index("▏"), (shell, result)
        display = "> " + native_expected + "\n"
        if shell == "zsh":
            # Zsh's default (COMBINING_CHARS unset) displays combining code points.
            display = "".join(
                f"<{ord(c):04x}>" if unicodedata.combining(c) else c for c in display
            )
        else:
            display = unicodedata.normalize("NFC", display)
        assert result.screen == display, (shell, result)
        parsed = CliRunner().invoke(unicode_fixture(), shlex.split(result.line)[1:])
        assert parsed.exit_code == 0, parsed.output
        words = shlex.split(expected.replace("▏", ""))[1:]
        if words[0].startswith("--value="):
            expected_value = words[0].partition("=")[2]
        elif words[0].startswith("-v") and words[0] != "--value":
            expected_value = words[0][2:]
        else:
            expected_value = words[1]
        assert parsed.stdout == expected_value + "\n"
        sections.append(
            f"Shell: {shell}\n\n{result.screen}\nBuffer: {json.dumps(result.line)}\nCursor: {result.cursor}\n"
        )
    actual = f"Input: {input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "unicode" / f"{name}.snap", actual
    )
