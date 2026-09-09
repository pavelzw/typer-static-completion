"""The screen harness must fail clearly and clean up stalled shells."""

import os
import shlex
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from snapshot_harness import capture, keystrokes


@pytest.mark.parametrize(
    "value", ["demo<ENTER>", "demo\n", "demo<TAB:0>", "demo<TAB:1001>"]
)
def test_invalid_keys(value):
    with pytest.raises(ValueError):
        keystrokes(value)


def test_editing_keys():
    assert (
        keystrokes("a<LEFT:2><TAB><BACKSPACE><RIGHT><HOME><END>")
        == "a\x02\x02\t\x7f\x06\x01\x05"
    )


def test_timeout_reaps_worker(tmp_path: Path):
    pid_file = tmp_path / "pid"
    shell = tmp_path / "stalled shell"
    shell.write_text(
        f"#!/bin/sh\nprintf '%s' \"$$\" > {shlex.quote(str(pid_file))}\nprintf 'startup stall'\nexec /bin/sleep 30\n"
    )
    shell.chmod(0o755)
    with pytest.raises(AssertionError, match="startup stall"):
        capture("", "demo", executable=str(shell), timeout=2)
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_file.read_text()), 0)


def test_static_invocation_is_detected():
    script = "_bad() { demo; }; complete -F _bad demo\n"
    with pytest.raises(AssertionError, match="invoked"):
        capture(script, "demo a<TAB>")


def test_output_is_bounded():
    from snapshot_harness import Transcript

    transcript = Transcript()
    with pytest.raises(AssertionError, match="exceeded"):
        transcript.write("x" * (1024 * 1024 + 1))


def test_startup_failure_retains_diagnostics(tmp_path):
    shell = tmp_path / "failed shell"
    shell.write_text("#!/bin/sh\nprintf 'startup failed'\nexit 1\n")
    shell.chmod(0o755)
    with pytest.raises(AssertionError, match="startup failed"):
        capture("", "demo", executable=str(shell))
