"""Knobs shared by every generator."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class DynamicPolicy(str, Enum):
    """What to do with parameters only the app can complete.

    A parameter with ``autocompletion=`` (recorded by typer as
    ``_custom_shell_complete``), or whose candidates depend on the context, has
    no static answer. There is no universally right response, so it is a choice:

    - :attr:`OMIT` -- offer nothing for that value. Fast and honest, but the
      user gets silence where they expect help.
    - :attr:`DELEGATE` -- emit a command substitution that calls back into the
      app using typer's own completion protocol. Only *that* parameter pays the
      interpreter startup; command names, flags and choices stay instant. This is
      the opt-in hybrid mode (not yet implemented).
    - :attr:`FILE` -- fall back to filesystem completion, which is what most
      shells would have done anyway.
    - :attr:`ERROR` -- refuse to generate. For projects that want a build-time
      guarantee the script is complete rather than a silent degradation.
    """

    OMIT = "omit"
    DELEGATE = "delegate"
    FILE = "file"
    ERROR = "error"


@dataclass(frozen=True)
class GenerationOptions:
    """Everything that changes the *content* of a generated script.

    Frozen and value-comparable so it can key a cache and so ``--check`` can
    prove it regenerated under the same settings as the committed file.
    """

    dynamic: DynamicPolicy = DynamicPolicy.OMIT
    #: Include one-line descriptions next to candidates. Only zsh and fish show
    #: them; bash ignores this. Turn off for smaller scripts.
    include_help: bool = True
    include_hidden: bool = False
    include_deprecated: bool = True
    #: Offer ``--help``. The flag and its aliases are read from the app
    #: (``add_help_option``, ``help_option_names``) rather than hardcoded, so an
    #: app that disables or renames it generates correctly.
    include_help_option: bool = True
    #: Emit a ``# Generated - do not edit`` banner naming the command below.
    banner: bool = True
    #: Command to print in the banner, e.g. ``"pixi run gen-completions"``.
    regenerate_command: str | None = None
    #: Stamp the library and typer versions into the banner. Off by default: it
    #: makes every dependency bump a diff in committed scripts.
    include_version: bool = False
    #: Extra ``ValueKind.OPAQUE`` parameter names to complete as files, matched
    #: against ``Param.name``. For params whose type does not reveal a path.
    file_params: frozenset[str] = field(default_factory=frozenset)
