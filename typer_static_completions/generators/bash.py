"""bash generator.

A single function with a ``case`` over the resolved subcommand path, registered
via ``complete -o default -F``. ``-o default`` lets bash fall back to filenames
when the function offers nothing.

bash has no per-option actions the way zsh's ``_arguments`` does, so choices need
a second dispatch keyed on ``"<cmdpath>|<flag just typed>"``, consulted before
the main one. Without it, ``app run --color <TAB>`` offers flags instead of
``red green blue``.
"""

from __future__ import annotations

from ..model import CommandTree
from ..shells import Shell
from .base import Generator


class BashGenerator(Generator):
    shell = Shell.bash
    install_layout = "share/bash-completion/completions/{prog}"
    filename = "{prog}"

    def render(self, tree: CommandTree) -> str:
        raise NotImplementedError

    def quote(self, text: str) -> str:
        raise NotImplementedError

    def _value_dispatch(self, tree: CommandTree) -> str:
        """The ``case "$cmdpath|$prev"`` block offering option values.

        Returns ``""`` when no parameter has static values, so simple apps do not
        carry a dead ``case`` with only a ``*)`` arm.
        """
        raise NotImplementedError
