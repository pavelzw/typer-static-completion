"""Capture real Bash, Fish, and Zsh sessions as a terminal screen, including cursor."""

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


class TerminalProtocol(Transcript):
    """Answer terminal capability queries while the interactive shell starts."""

    query = re.compile(
        r"\x1b\[[0-?]*[ -/]*[@-~]|\x1b\]11;\?(?:\x07|\x1b\\)|\x1bP\+q[^\x1b]*\x1b\\"
    )

    def __init__(self, send):
        super().__init__()
        self.send = send
        self.pending = ""
        self.screen = pyte.Screen(80, 24)
        self.stream = pyte.Stream(self.screen)

    def write(self, value: str):
        super().write(value)
        self.pending += value
        end = 0
        for match in self.query.finditer(self.pending):
            self.stream.feed(self.pending[end : match.start()])
            query = match[0]
            if not re.match(r"\x1b(?:\[[>=]|P)", query):
                self.stream.feed(query)
            response = ""
            if query in ("\x1b[c", "\x1b[0c"):
                response = "\x1b[?1;2c"
            elif query in ("\x1b[>c", "\x1b[>0c"):
                response = "\x1b[>0;370;0c"
            elif query == "\x1b[6n":
                response = (
                    f"\x1b[{self.screen.cursor.y + 1};{self.screen.cursor.x + 1}R"
                )
            elif query == "\x1b[5n":
                response = "\x1b[0n"
            elif query == "\x1b[?u":
                response = "\x1b[?0u"
            elif query in ("\x1b[>q", "\x1b[>0q"):
                response = "\x1bP>|XTerm(370)\x1b\\"
            elif query.startswith("\x1b]11;"):
                response = "\x1b]11;rgb:0000/0000/0000\x1b\\"
            elif query.startswith("\x1bP+q"):
                response = "\x1bP0+r" + query[4:]
            if response:
                self.send(response)
            end = match.end()
        self.pending = self.pending[end:]


def capture(
    script: str,
    input: str,
    *,
    shell: str = "bash",
    executable: str | None = None,
    timeout: float = 10,
) -> str:
    keys = keystrokes(input)
    if shell not in ("bash", "fish", "zsh"):
        raise ValueError(f"Unsupported shell: {shell}")
    executable = executable or shutil.which(shell)
    if not executable:
        raise RuntimeError(
            f"{shell} is required; run pixi run -e snapshots test-snapshots"
        )
    transcript = ""
    with TemporaryDirectory(prefix="tsc-screen-") as directory:
        cwd = Path(directory)
        (cwd / "home").mkdir()
        (cwd / "nested directory").mkdir()
        (cwd / "two words.json").touch()
        (cwd / "quote's.json").touch()
        setup = cwd / "setup"
        if shell == "bash":
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
            args = ["--noprofile", "--rcfile", str(setup), "-i"]
        elif shell == "zsh":
            setup.write_text(
                "autoload -Uz compinit\ncompinit -D -u\n"
                + script
                + r"""
PROMPT='> '
RPROMPT=
setopt NO_BEEP
unsetopt AUTO_MENU MENU_COMPLETE
bindkey -e
zstyle ':completion:*' list-colors ''
_mark() { printf '\033]777;TSC_DONE\007'; }
zle -N _mark
bindkey '^X^G' _mark
demo() { printf invoked > invoked; }
python() { printf invoked > invoked; }
python3() { printf invoked > invoked; }
PATH=/nonexistent
zle-line-init() { printf '\033]777;TSC_READY\007'; zle reset-prompt; }
zle -N zle-line-init
"""
            )
            args = ["-f", "-i"]
        else:
            setup.write_text(
                "set -g fish_complete_path\n"
                + script
                + r"""
set -g fish_greeting
set -g fish_autosuggestion_enabled 0
set -g fish_key_bindings fish_default_key_bindings
function fish_prompt; printf '> '; end
function fish_right_prompt; end
function fish_title; end
bind ctrl-x,ctrl-g "printf '\033]777;TSC_DONE\007'"
function demo; printf invoked > invoked; end
function python; printf invoked > invoked; end
function python3; printf invoked > invoked; end
set -gx PATH /nonexistent
printf '\033]777;TSC_READY\007'
"""
            )
            args = ["--no-config", "--interactive", "--init-command", "source ./setup"]
        env = {
            "HOME": str(cwd / "home"),
            "ZDOTDIR": str(cwd / "home"),
            "XDG_CONFIG_HOME": str(cwd / "home"),
            "XDG_DATA_HOME": str(cwd / "home"),
            "PS1": "TSC_BOOT> ",
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
            args,
            cwd=directory,
            env=env,
            encoding="utf-8",
            dimensions=(24, 80),
            timeout=timeout,
        )
        child.delaybeforesend = None
        protocol = TerminalProtocol(child.send)
        child.logfile_read = protocol
        deadline = time.monotonic() + timeout
        try:
            if shell == "zsh":
                child.expect_exact("TSC_BOOT> ", timeout=timeout)
                child.send("source ./setup\r")
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
            if shell == "bash":
                screen_output = re.sub(r"\r\x1b\[K\r$|\r?\n$", "", screen_output)
            elif shell == "fish":
                # expect may have already read past the acknowledgement.
                screen_output += child.buffer
                # Fish redraws after running the capture binding. Drain that
                # output before rendering the final screen.
                while time.monotonic() < deadline:
                    try:
                        screen_output += child.read_nonblocking(65536, timeout=0.1)
                    except pexpect.TIMEOUT:
                        break
            screen = pyte.Screen(80, 24)
            # pyte models VT terminals; Kitty keyboard-mode toggles and
            # capability DCS messages do not draw on the screen.
            screen_output = re.sub(
                r"\x1b\[[>=][0-9;]*[a-zA-Z]|\x1bP.*?\x1b\\", "", screen_output
            )
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
                f"{shell} snapshot failed or timed out after {timeout}s: {input!r}\n{transcript!r}"
            ) from exc
        finally:
            # The PTY child starts a new session. Kill its process group so a
            # startup script cannot leave descendants behind after a timeout.
            try:
                os.killpg(child.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            except PermissionError:
                # macOS can report EPERM after the PTY process has exited.
                # Preserve the startup failure rather than masking it.
                if child.isalive():
                    raise
            child.close(force=True)
