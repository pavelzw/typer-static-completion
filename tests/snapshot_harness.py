"""Capture a real Bash Readline session as a terminal screen, including cursor."""

from __future__ import annotations

import os
import re
import shutil
import signal
import time
from pathlib import Path
from tempfile import TemporaryDirectory

import pexpect  # type: ignore[import-untyped]
import pyte  # type: ignore[import-not-found]

KEYS = {
    "TAB": "\t",
    "LEFT": "\x02",
    "RIGHT": "\x06",
    "HOME": "\x01",
    "END": "\x05",
    "BACKSPACE": "\x7f",
}
READY = "\x1b]777;TSC_READY\x07"
DONE = "\x1b]777;TSC_DONE\x07"


def keystrokes(value: str) -> str:
    if re.search(r"[\x00-\x1f\x7f]", value):
        raise ValueError("Use named keys, not raw control characters")

    def replace(match: re.Match[str]) -> str:
        key, count = match[1], int(match[2] or 1)
        if key not in KEYS or not 1 <= count <= 1000:
            raise ValueError(f"Invalid keystroke: {match[0]}")
        return KEYS[key] * count

    return re.sub(r"<([A-Z]+)(?::(\d+))?>", replace, value)


class Transcript:
    """Keep actionable diagnostics while bounding terminal output."""

    def __init__(self):
        self.parts: list[str] = []
        self.size = 0

    def write(self, value: str):
        self.size += len(value)
        if self.size > 1024 * 1024:
            raise AssertionError("Terminal output exceeded 1 MiB")
        self.parts.append(value)

    def flush(self):
        pass


def capture(
    script: str, input: str, *, executable: str | None = None, timeout: float = 5
) -> str:
    keys = keystrokes(input)
    executable = executable or shutil.which("bash")
    if not executable:
        raise RuntimeError("Bash is required; run pixi run -e snapshots test-snapshots")
    transcript = ""
    with TemporaryDirectory(prefix="tsc-screen-") as directory:
        cwd = Path(directory)
        (cwd / "home").mkdir()
        (cwd / "nested directory").mkdir()
        (cwd / "two words.json").touch()
        (cwd / "quote's.json").touch()
        setup = cwd / "setup"
        setup.write_text(
            script
            + r"""
set -o emacs
PS1='\[\e]777;TSC_READY\a\]> '
PS2='... '
PROMPT_COMMAND=
HISTFILE=/dev/null
bind 'set enable-bracketed-paste off'
bind 'set show-all-if-ambiguous off'
bind 'set page-completions off'
bind 'set completion-query-items 0'
bind 'set bell-style none'
_mark() { printf '\033]777;TSC_DONE\007'; }
bind -x '"\C-x\C-g":_mark'
demo() { printf invoked > invoked; }
python() { printf invoked > invoked; }
python3() { printf invoked > invoked; }
PATH=/nonexistent
"""
        )
        env = {
            "HOME": str(cwd / "home"),
            "TERM": "xterm",
            "LC_ALL": "C",
            "INPUTRC": "/dev/null",
            "HISTFILE": "/dev/null",
            "PATH": os.defpath,
            "COLUMNS": "80",
            "LINES": "24",
        }
        child = pexpect.spawn(
            executable,
            ["--noprofile", "--rcfile", str(setup), "-i"],
            cwd=directory,
            env=env,
            encoding="utf-8",
            dimensions=(24, 80),
            timeout=timeout,
        )
        child.delaybeforesend = None
        child.logfile_read = Transcript()
        deadline = time.monotonic() + timeout
        try:
            child.expect_exact(READY, timeout=max(0, deadline - time.monotonic()))
            transcript += child.before
            child.send(keys + "\x18\x07")
            child.expect_exact(DONE, timeout=max(0, deadline - time.monotonic()))
            screen_output = child.before
            transcript += screen_output
            if (cwd / "invoked").exists():
                raise AssertionError("Static completion invoked the CLI or Python")
            # Bash clears the editing line before bind -x runs. Exclude that
            # capture-binding artifact, retaining the actual completion redraw.
            screen_output = re.sub(r"\r\x1b\[K\r$|\r?\n$", "", screen_output)
            screen = pyte.Screen(80, 24)
            pyte.Stream(screen).feed(screen_output)
            lines = list(screen.display)
            row, column = screen.cursor.y, screen.cursor.x
            lines[row] = lines[row][:column] + "▏" + lines[row][column:]
            lines = [line.rstrip() for line in lines]
            while lines and not lines[-1]:
                lines.pop()
            return "\n".join(lines) + "\n"
        except (pexpect.TIMEOUT, pexpect.EOF) as exc:
            transcript += child.before
            raise AssertionError(
                f"Bash snapshot failed or timed out after {timeout}s: {input!r}\n{transcript!r}"
            ) from exc
        finally:
            # The PTY child starts a new session. Kill its process group so a
            # startup script cannot leave descendants behind after a timeout.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            child.close(force=True)
