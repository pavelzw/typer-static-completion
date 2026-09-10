"""Shell identifiers.

:class:`Shell` is a ``str`` enum, so the members interoperate with plain strings
everywhere a shell is accepted. Third-party generators may register shells that
are not members here (see :mod:`typer_static_completion.generators`), which is
why the public API is typed as ``str | Shell`` rather than ``Shell``.
"""

from __future__ import annotations

from enum import Enum
from typing import TypeAlias


class Shell(str, Enum):
    """Shells with a built-in generator."""

    bash = "bash"
    fish = "fish"
    zsh = "zsh"


#: Shells generated when a caller does not narrow the selection.
DEFAULT_SHELLS: tuple[Shell, ...] = (Shell.bash, Shell.zsh, Shell.fish)

#: Anything accepted where a shell is expected.
ShellName: TypeAlias = "str | Shell"
