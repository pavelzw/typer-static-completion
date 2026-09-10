"""Check generated scripts with the installed shell's syntax parser.

Behavioral completion checks live in the test suite's native shell and interactive
screen harnesses; syntax validation alone does not prove candidate correctness.
"""

from __future__ import annotations

import shutil
import subprocess

from .errors import ScriptSyntaxError, ShellUnavailableError, UnsupportedShellError
from .shells import ShellName


def check_syntax(script: str, shell: ShellName) -> None:
    """Parse ``script`` with the shell's own parser.

    Raises:
        ScriptSyntaxError: if the shell rejects the script; the message carries
            the shell's stderr.
        ShellUnavailableError: if the shell binary is not installed.
    """
    if shell not in ("bash", "fish", "zsh"):
        raise UnsupportedShellError(
            f"Syntax verification is not implemented for {shell!r}"
        )
    executable = shutil.which(shell)
    if not executable:
        raise ShellUnavailableError(f"{shell} is not installed")
    result = subprocess.run(
        [executable, "-n"],
        input=script,
        text=True,
        encoding="utf-8",
        capture_output=True,
        timeout=10,
    )
    if result.returncode:
        raise ScriptSyntaxError(result.stderr.strip())


def is_available(shell: ShellName) -> bool:
    """Whether the shell binary needed to verify this shell is installed."""
    return shutil.which(shell) is not None
