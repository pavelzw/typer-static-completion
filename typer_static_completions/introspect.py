"""Build a :class:`~typer_static_completions.model.CommandTree` from an app.

This is the *only* module that touches typer's internals. Since typer 0.26 click
is vendored under ``typer._click``, so a ``TyperGroup`` is not an
``isinstance`` of upstream ``click.Command`` -- which is exactly why ``shtab``
cannot be used here, and why the accesses below are pinned to typer rather than
click.

Four attribute-level traps, each of which silently produces a *plausible but
wrong* script rather than an error:

- Select options by ``param_type_name == "option"``, never by truthiness of
  ``p.opts``: positional arguments carry ``opts`` too (it holds the argument
  name), so filtering on it emits bogus short flags like ``-s ame`` for a
  ``name: str`` argument.
- Include ``p.secondary_opts``: a ``bool`` option yields ``--loud`` *and*
  ``--no-loud``, and the second lives only there.
- Detect file-ish parameters via ``p.type.name``, not ``isinstance``: ``Path``
  becomes ``TyperPath(name="path")`` and ``typer.FileText`` becomes
  ``File(name="filename")``. Matching the name avoids importing private classes.
- Choices come from ``typer._types.TyperChoice``; ``typer._click.types`` has no
  ``Choice`` at all.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .model import CommandTree

if TYPE_CHECKING:
    import typer


#: ``type.name`` values that should fall back to real filesystem completion.
FILE_TYPE_NAMES: frozenset[str] = frozenset({"path", "file", "filename"})

#: ``type.name`` values completed as directories only.
DIRECTORY_TYPE_NAMES: frozenset[str] = frozenset({"directory"})


def from_app(
    app: typer.Typer,
    prog_name: str,
    *,
    include_hidden: bool = False,
    include_deprecated: bool = True,
    max_depth: int | None = None,
) -> CommandTree:
    """Introspect a ``Typer`` app.

    Args:
        app: The application. Converted via ``typer.main.get_command``, so a
            single-command app (one ``@app.command()``, no group) is handled the
            same as a multi-command one.
        prog_name: The name users type. Not derivable from the app itself --
            it comes from ``[project.scripts]`` or the caller.
        include_hidden: Emit commands and options marked ``hidden=True``.
        include_deprecated: Emit deprecated commands and options. Keep them by
            default: they still work, so completing them is honest.
        max_depth: Stop walking below this depth. ``None`` means unlimited.

    Raises:
        IntrospectionError: if the command tree cannot be read.
    """
    raise NotImplementedError


def from_command(
    command: Any,
    prog_name: str,
    *,
    include_hidden: bool = False,
    include_deprecated: bool = True,
    max_depth: int | None = None,
) -> CommandTree:
    """Introspect an already-converted ``typer._click.Command``.

    Escape hatch for callers who build their command object themselves (a
    ``TyperGroup`` assembled by hand, or a click ``Group`` that typer wrapped).
    Typed as ``Any`` deliberately: naming the vendored class in a public
    signature would leak a private import into every caller's type checking.

    Raises:
        IntrospectionError: if the object is not a command-like object.
    """
    raise NotImplementedError


def load_app(target: str) -> typer.Typer:
    """Import a ``"module:attribute"`` target and return the app.

    Also accepts a bare ``"module"``, in which case a module-level ``app``,
    ``cli`` or ``main`` attribute is used, in that order.

    Note that this *imports the target module*, running its side effects, in the
    current interpreter. For an app that is expensive or unsafe to import in the
    build environment, generate in a subprocess instead.

    Raises:
        AppLoadError: if the import fails, the attribute is missing, or the
            object is neither a ``Typer`` app nor a command.
    """
    raise NotImplementedError


def entrypoints(pyproject: Any = None) -> dict[str, str]:
    """Read ``[project.scripts]`` as ``{prog_name: "module:attribute"}``.

    Args:
        pyproject: Path to a ``pyproject.toml``. Defaults to the nearest one at
            or above the current directory.

    Raises:
        AppLoadError: if the file is missing or has no ``[project.scripts]``.
    """
    raise NotImplementedError
