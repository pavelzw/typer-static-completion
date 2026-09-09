"""The generator contract.

A generator turns a :class:`~typer_static_completions.model.CommandTree` into
one shell's script text. Generators read only the model and
:class:`~typer_static_completions.config.GenerationOptions` -- never a ``Typer``
app -- so they can be unit-tested against hand-built trees.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import replace

from ..config import GenerationOptions
from ..errors import IntrospectionError
from ..model import CommandTree, Param


class Generator(ABC):
    """Base class for shell script generators."""

    #: Shell this generator produces scripts for.
    shell: str

    #: Where the shell looks for completion files, relative to an install root,
    #: with ``{prog}`` substituted. E.g. ``"share/fish/vendor_completions.d/\
    #: {prog}.fish"``.
    install_layout: str

    #: Filename inside a flat output directory, with ``{prog}`` substituted.
    #: zsh requires the leading underscore (``_{prog}``); the others do not care.
    filename: str

    def __init__(self, options: GenerationOptions | None = None) -> None:
        self.options = options or GenerationOptions()

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


def value_slots(param: Param) -> tuple[Param, ...]:
    """Flatten option values into consecutive parser targets."""
    if param.flags and param.nargs > 1:
        if len(param.values) != param.nargs:
            raise IntrospectionError("Tuple options require metadata for every value")
        return tuple(
            replace(
                param,
                value_kind=value.value_kind,
                choices=value.choices,
                values=(),
                nargs=1,
            )
            for value in param.values
        )
    if param.nargs not in (1, -1) or (param.flags and param.nargs != 1):
        raise IntrospectionError(
            "Only scalar/tuple options and scalar/variadic arguments are supported yet"
        )
    return (param,)
