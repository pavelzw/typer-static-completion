"""PowerShell generator.

Unlike the POSIX shells, PowerShell has no directory it scans for completion
files. The output is a ``Register-ArgumentCompleter -Native`` block that the user
dot-sources from their ``$PROFILE``, so :attr:`PowerShellGenerator.install_layout`
points at a profile fragment rather than a completions directory.

Candidates are emitted as ``[CompletionResult]`` objects, which carry a tooltip,
so help text survives here even though it is a single flat script. Covers both
Windows PowerShell 5.1 and cross-platform ``pwsh``.
"""

from __future__ import annotations

from ..model import CommandTree
from ..shells import Shell
from .base import Generator


class PowerShellGenerator(Generator):
    shell = Shell.powershell
    install_layout = "share/powershell/completions/{prog}.ps1"
    filename = "{prog}.ps1"

    def render(self, tree: CommandTree) -> str:
        raise NotImplementedError

    def quote(self, text: str) -> str:
        """Escape for a single-quoted PowerShell string (``'`` doubled)."""
        raise NotImplementedError
