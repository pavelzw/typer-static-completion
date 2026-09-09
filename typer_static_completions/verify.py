"""Check that a generated script actually works.

Do not trust a generated script that has only been eyeballed. Two levels:

- :func:`check_syntax` -- ``bash -n`` / ``zsh -n`` / ``fish -n``. Cheap, catches
  shell syntax errors, and worth running in the library's own test suite for a
  matrix of synthetic apps.
- :func:`complete` -- actually drive the completion engine and return the
  candidates for a given command line. This is what proves the *dispatch* is
  right, which syntax checking cannot.

:func:`complete` needs the real shell installed, so tests using it should skip
when it is missing rather than fail.

Per-shell mechanics:

- **fish** has ``complete -C "<line>"``, which runs the real engine. Exact.
- **bash** requires faking ``COMP_WORDS``/``COMP_CWORD`` and calling the function,
  then reading ``COMPREPLY``.
- **zsh** is exercised through a real interactive PTY in the test suite. The
  public :func:`complete` helper is still unimplemented; it must not substitute
  mocked dispatch results for real candidates.

Note that fish only offers option flags once the current token starts with
``-``; an empty token after a command shows subcommands and files. That is fish
being fish, not a bug in the script -- assertions have to account for it.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

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
        capture_output=True,
        timeout=10,
    )
    if result.returncode:
        raise ScriptSyntaxError(result.stderr.strip())


def is_available(shell: ShellName) -> bool:
    """Whether the shell binary needed to verify this shell is installed."""
    return (
        shutil.which("pwsh" if shell in ("powershell", "pwsh") else shell) is not None
    )


@dataclass(frozen=True)
class Completion:
    """What a shell offered for one command line."""

    #: Candidate words, in the order the shell produced them.
    candidates: tuple[str, ...]
    #: Descriptions by candidate, where the shell reports them (zsh, fish).
    descriptions: dict[str, str]
    #: Raw shell output, for debugging a surprising result.
    raw: str


def complete(
    script: str | Path,
    shell: ShellName,
    command_line: str,
    *,
    prog_name: str | None = None,
) -> Completion:
    """Run ``script`` in ``shell`` and return the candidates for ``command_line``.

    Args:
        script: Script text, or a path to one.
        command_line: What the user has typed, cursor at the end. A trailing
            space means "starting a new word" and is significant -- ``"app "``
            and ``"app"`` complete differently.
        prog_name: Needed for shells where the completion function must be called
            by name (bash). Inferred from the script when omitted.

    Raises:
        ShellUnavailableError: if the shell is not installed.
        ScriptSyntaxError: if the script fails to load.

    Example:
        >>> complete(script, "fish", "myapp items ").candidates
        ('ls', 'rm')
    """
    raise NotImplementedError
