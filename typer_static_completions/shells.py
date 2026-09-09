"""Shell identifiers.

:class:`Shell` is a ``str`` enum, so the members interoperate with plain strings
everywhere a shell is accepted. Third-party generators may register shells that
are not members here (see :mod:`typer_static_completions.generators`), which is
why the public API is typed as ``str | Shell`` rather than ``Shell``.
"""

from __future__ import annotations

from enum import Enum
from typing import TypeAlias


class Shell(str, Enum):
    """Shells with a built-in generator."""

    bash = "bash"
    zsh = "zsh"
    fish = "fish"
    powershell = "powershell"

    @classmethod
    def parse(cls, value: str | Shell) -> Shell:
        """Coerce a shell name to a member, accepting ``pwsh`` for PowerShell.

        Raises:
            UnsupportedShellError: if ``value`` is not a known member.
        """
        raise NotImplementedError

    @classmethod
    def current(cls) -> Shell:
        """Best-effort guess of the shell that invoked this process.

        Reads ``$SHELL`` and the parent process name, mirroring what typer's
        ``--install-completion`` does.

        Raises:
            UnsupportedShellError: if the shell cannot be determined.
        """
        raise NotImplementedError


#: Shells generated when a caller does not narrow the selection.
#:
#: PowerShell is excluded: its completion model is a single ``Register-Argument\
#: Completer`` block rather than a file the shell picks up on its own, so it is
#: opt-in.
DEFAULT_SHELLS: tuple[Shell, ...] = (Shell.bash, Shell.zsh, Shell.fish)

#: Anything accepted where a shell is expected.
ShellName: TypeAlias = "str | Shell"
