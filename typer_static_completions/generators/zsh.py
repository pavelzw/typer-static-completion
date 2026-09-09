"""zsh generator.

The richest output of the four: zsh's ``_arguments`` handles per-option values,
positional slots and descriptions natively, so most of the work is emitting
correct specs.

Three things here are load-bearing, and each one fails *silently* -- completing
nothing at all, with no error:

- **Shift ``words`` past the resolved subcommand path.** ``_arguments`` reads
  ``words``/``CURRENT`` directly and counts positionals from ``words[2]``. Both
  are the caller's locals, so shifting them is what makes the specs line up;
  without it every subcommand word is an unexpected positional and ``_arguments``
  bails out.
- **Emit positional specs.** With no ``N:name:action`` spec, ``_arguments``
  treats a bare word as an error and gives up -- taking the option completions
  down with it. A variadic argument is ``*:``, not a numbered slot.
- **One spec per flag, not zsh's ``{-a,--long}`` shorthand.** That form relies on
  brace expansion, so it only works unquoted -- but specs must be quoted to
  survive spaces and colons in help text. A ``(-a --long)`` exclusion prefix
  restores the mutual exclusivity the shorthand provided.

Subcommands are dispatched through ``_arguments -C`` and a ``->subcommand``
state, then described with ``_describe``. Treating the subcommand as a *named
positional slot* keeps it from fighting the command's own positionals.
"""

from __future__ import annotations

from ..model import Command, CommandTree
from ..shells import Shell
from .base import Generator


class ZshGenerator(Generator):
    shell = Shell.zsh
    install_layout = "share/zsh/site-functions/_{prog}"
    filename = "_{prog}"

    def render(self, tree: CommandTree) -> str:
        raise NotImplementedError

    def quote(self, text: str) -> str:
        """Escape for a single-quoted ``_arguments`` spec.

        Doubles ``'`` and backslash-escapes ``[``, ``]`` and ``:``, which are
        spec syntax rather than text.
        """
        raise NotImplementedError

    def _option_specs(self, command: Command, tree: CommandTree) -> list[str]:
        """``_arguments`` specs for the command's options."""
        raise NotImplementedError

    def _positional_specs(self, command: Command, tree: CommandTree) -> list[str]:
        """``N:name:action`` specs, plus the ``->subcommand`` slot if it's a group."""
        raise NotImplementedError
