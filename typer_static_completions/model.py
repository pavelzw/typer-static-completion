"""Shell-agnostic description of a CLI.

This is the seam of the library. :mod:`typer_static_completions.introspect`
builds these objects out of typer's (private) command classes; generators read
*only* these objects and never import typer. That keeps every version-fragile
attribute access in one module, and makes generators testable without
constructing a real ``Typer`` app.

Model fields are frozen. Commands copy their subcommand mappings and expose them
read-only, preserving insertion order. Command trees remain unhashable; use
dataclasses.replace() to build a modified tree.
"""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType


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
class ValueSpec:
    """Static completion metadata for one position in a tuple option."""

    value_kind: ValueKind
    choices: tuple[str, ...] = ()


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
    #: ``1`` for a scalar, tuple arity, or :data:`VARIADIC` for ``list[...]``.
    nargs: int = 1
    #: True if the option may be repeated (``multiple=True``); shells that
    #: normally suppress an already-seen flag must not do so for these.
    multiple: bool = False
    hidden: bool = False
    deprecated: bool = False
    is_help: bool = False
    #: Per-position metadata for a tuple option; empty for scalar parameters.
    values: tuple[ValueSpec, ...] = ()

    @property
    def takes_value(self) -> bool:
        """Whether a value follows the flag."""
        return self.value_kind is not ValueKind.FLAG

    @property
    def is_dynamic(self) -> bool:
        return self.value_kind is ValueKind.DYNAMIC or any(
            value.value_kind is ValueKind.DYNAMIC for value in self.values
        )


@dataclass(frozen=True)
class Command:
    """One node of the command tree.

    ``is_group`` preserves empty groups. A single-command Typer app collapses
    to a leaf root; hand-built nodes with subcommands also behave as groups.
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
    is_group: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "subcommands", MappingProxyType(dict(self.subcommands))
        )

    @property
    def name(self) -> str:
        """Last path segment, or ``""`` for the root."""
        return self.path[-1] if self.path else ""

    @property
    def options(self) -> tuple[Param, ...]:
        """Options retained by introspection, in declaration order."""
        return tuple(p for p in self.params if p.kind is ParamKind.OPTION)

    @property
    def arguments(self) -> tuple[Param, ...]:
        """Arguments retained by introspection, in declaration order."""
        return tuple(p for p in self.params if p.kind is ParamKind.ARGUMENT)

    def walk(self) -> Iterator[Command]:
        """Yield this node and every descendant, depth-first, root first."""
        yield self
        for child in self.subcommands.values():
            yield from child.walk()


@dataclass(frozen=True)
class CommandTree:
    """A whole application, as invoked under one program name."""

    #: The name users type, e.g. ``"my-cli"``. Also the completion file's name.
    prog_name: str
    root: Command

    def walk(self) -> Iterator[Command]:
        return self.root.walk()

    def paths(self) -> tuple[str, ...]:
        """Every reachable subcommand path, space-joined, excluding the root.

        Generated scripts bake this in to resolve which command the cursor is
        in. Resolving by "non-flag words before the cursor" instead is wrong:
        option values and positional arguments are non-flag words too.
        """
        return tuple(" ".join(c.path) for c in self.walk() if c.path)

    def find(self, path: Sequence[str]) -> Command | None:
        """Look up a command by path, or ``None`` if it does not exist."""
        node = self.root
        for name in path:
            if name not in node.subcommands:
                return None
            node = node.subcommands[name]
        return node

    @property
    def has_dynamic_params(self) -> bool:
        return any(p.is_dynamic for c in self.walk() for p in c.params)
