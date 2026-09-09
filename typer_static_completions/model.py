"""Shell-agnostic description of a CLI.

This is the seam of the library. :mod:`typer_static_completions.introspect`
builds these objects out of typer's (private) command classes; generators read
*only* these objects and never import typer. That keeps every version-fragile
attribute access in one module, and makes generators testable without
constructing a real ``Typer`` app.

Dataclass fields are frozen, but nested mappings are currently mutable and make
command trees unhashable. Deep immutability is still an open design task.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum


class ValueKind(str, Enum):
    """What a parameter accepts, reduced to what a shell can act on."""

    #: A boolean flag; takes no value at all.
    FLAG = "flag"
    #: Takes a value, but nothing static can be said about it.
    OPAQUE = "opaque"
    #: One of a fixed set of strings (an ``Enum`` or ``TyperChoice``).
    CHOICE = "choice"
    #: A filesystem path; defer to the shell's own file completion.
    FILE = "file"
    #: A directory path; defer to the shell's directory completion.
    DIRECTORY = "directory"
    #: Only the app itself can enumerate candidates (``autocompletion=``).
    #: How this is rendered depends on :class:`DynamicPolicy`.
    DYNAMIC = "dynamic"


class ParamKind(str, Enum):
    """Whether a parameter is selected by a flag or by position."""

    OPTION = "option"
    ARGUMENT = "argument"


#: ``nargs`` value typer/click use for a variadic parameter.
VARIADIC = -1


@dataclass(frozen=True)
class Param:
    """A single option or positional argument."""

    kind: ParamKind
    #: Attribute name; used to label the value in shells that show one (zsh).
    name: str
    value_kind: ValueKind
    #: Every flag that selects this option, ``--no-x`` forms included, in the
    #: order they should be offered. Empty for :attr:`ParamKind.ARGUMENT`.
    flags: tuple[str, ...] = ()
    #: The subset of :attr:`flags` that sets the value to false. Generators that
    #: mark aliases mutually exclusive need to know these are not aliases.
    negation_flags: tuple[str, ...] = ()
    #: Populated only when :attr:`value_kind` is :attr:`ValueKind.CHOICE`.
    choices: tuple[str, ...] = ()
    #: First line of the help text, already stripped. Never ``None``; use ``""``
    #: for absent, so generators do not each re-implement the fallback.
    help: str = ""
    metavar: str | None = None
    required: bool = False
    #: ``1`` for a scalar, :data:`VARIADIC` for ``list[...]``.
    nargs: int = 1
    #: True if the option may be repeated (``multiple=True``); shells that
    #: normally suppress an already-seen flag must not do so for these.
    multiple: bool = False
    hidden: bool = False
    deprecated: bool = False

    @property
    def takes_value(self) -> bool:
        """Whether a value follows the flag."""
        raise NotImplementedError

    @property
    def is_dynamic(self) -> bool:
        raise NotImplementedError


@dataclass(frozen=True)
class Command:
    """One node of the command tree.

    A node is a group exactly when :attr:`subcommands` is non-empty; there is no
    separate type, because a typer app with a single command collapses to a leaf
    root and generators should handle that without a special case.
    """

    #: Path from the root, excluding the program name. Empty tuple for the root.
    path: tuple[str, ...]
    help: str = ""
    params: tuple[Param, ...] = ()
    #: Insertion-ordered; typer preserves declaration order and so do we.
    subcommands: Mapping[str, Command] = field(default_factory=dict)
    hidden: bool = False
    deprecated: bool = False
    #: True for ``chain=True`` groups, where several subcommands may be given in
    #: one invocation. Generators must keep offering siblings after the first.
    chain: bool = False

    @property
    def name(self) -> str:
        """Last path segment, or ``""`` for the root."""
        raise NotImplementedError

    @property
    def options(self) -> tuple[Param, ...]:
        """Visible options, in declaration order."""
        raise NotImplementedError

    @property
    def arguments(self) -> tuple[Param, ...]:
        """Visible positional arguments, in declaration order."""
        raise NotImplementedError

    def walk(self) -> Iterator[Command]:
        """Yield this node and every descendant, depth-first, root first."""
        raise NotImplementedError


@dataclass(frozen=True)
class CommandTree:
    """A whole application, as invoked under one program name."""

    #: The name users type, e.g. ``"my-cli"``. Also the completion file's name.
    prog_name: str
    root: Command
    #: Set when the app has ``autocompletion=`` callbacks anywhere; a generator
    #: honouring :attr:`DynamicPolicy.DELEGATE` needs it to build the env var.
    complete_var: str | None = None

    def walk(self) -> Iterator[Command]:
        raise NotImplementedError

    def paths(self) -> tuple[str, ...]:
        """Every reachable subcommand path, space-joined, excluding the root.

        Generated scripts bake this in to resolve which command the cursor is
        in. Resolving by "non-flag words before the cursor" instead is wrong:
        option values and positional arguments are non-flag words too.
        """
        raise NotImplementedError

    def find(self, path: Sequence[str]) -> Command | None:
        """Look up a command by path, or ``None`` if it does not exist."""
        raise NotImplementedError

    @property
    def has_dynamic_params(self) -> bool:
        raise NotImplementedError
