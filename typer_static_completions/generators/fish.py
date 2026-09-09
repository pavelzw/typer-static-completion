"""fish generator.

fish has no dispatch function: completions are a flat list of ``complete -c``
rules, each guarded by a ``-n`` condition. So the script defines two helpers --
one resolving the current subcommand path against the baked-in valid paths, one
comparing it -- and every rule is conditioned on the latter.

The naive condition ``__fish_seen_subcommand_from items`` does not work: it stays
true at deeper levels, so ``app items ls <TAB>`` keeps re-offering ``ls``.

``-f`` (no file completion) must go on individual subcommand rules, never on a
global ``complete -c app -f``, which would also suppress file completion for
positional arguments that legitimately want paths.
"""

from __future__ import annotations

from ..model import CommandTree
from ..shells import Shell
from .base import Generator


class FishGenerator(Generator):
    shell = Shell.fish
    install_layout = "share/fish/vendor_completions.d/{prog}.fish"
    filename = "{prog}.fish"

    def render(self, tree: CommandTree) -> str:
        raise NotImplementedError

    def quote(self, text: str) -> str:
        """Escape for a double-quoted fish string (``\\``, ``"``, ``$``, `````)."""
        raise NotImplementedError

    def _helpers(self, tree: CommandTree) -> list[str]:
        """The ``__<prog>_cmdpath`` / ``__<prog>_at`` helper functions.

        Names are derived from the program name with ``-`` and ``.`` replaced, so
        two CLIs installed side by side do not collide.
        """
        raise NotImplementedError
