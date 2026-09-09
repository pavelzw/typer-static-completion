"""The generator contract.

A generator turns a :class:`~typer_static_completions.model.CommandTree` into
one shell's script text. Generators read only the model and
:class:`~typer_static_completions.config.GenerationOptions` -- never a ``Typer``
app -- so they can be unit-tested against hand-built trees.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..config import GenerationOptions
from ..model import CommandTree, Param
from ..shells import Shell


class Generator(ABC):
    """Base class for shell script generators."""

    #: Shell this generator produces scripts for.
    shell: Shell

    #: Where the shell looks for completion files, relative to an install root,
    #: with ``{prog}`` substituted. E.g. ``"share/fish/vendor_completions.d/\
    #: {prog}.fish"``.
    install_layout: str

    #: Filename inside a flat output directory, with ``{prog}`` substituted.
    #: zsh requires the leading underscore (``_{prog}``); the others do not care.
    filename: str

    def __init__(self, options: GenerationOptions | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def render(self, tree: CommandTree) -> str:
        """Return the complete script text, ending in a newline."""

    @abstractmethod
    def quote(self, text: str) -> str:
        """Escape ``text`` for interpolation into this shell's script.

        Not cosmetic: help texts routinely contain quotes and colons, and zsh's
        ``_arguments`` treats ``[``, ``]`` and ``:`` as syntax, so a help string
        like ``List items ("all" by default)`` corrupts an unescaped script.
        """

    def value_action(self, param: Param, tree: CommandTree) -> str:
        """Render what to offer for ``param``'s value.

        Dispatches on :attr:`~typer_static_completions.model.Param.value_kind`
        and on :class:`~typer_static_completions.config.DynamicPolicy`; the
        per-shell spelling is the subclass's job.
        """
        raise NotImplementedError

    def install_path(self, prog_name: str, root: str | None = None) -> str:
        """Where this script belongs on a real system."""
        raise NotImplementedError
