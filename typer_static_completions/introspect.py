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

from .errors import IntrospectionError
from .model import Command, CommandTree, Param, ParamKind, ValueKind, ValueSpec

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
    from typer.main import get_command, solve_typer_info_defaults
    from typer.models import TyperInfo

    def reject_chain(info: Any) -> None:
        # Typer 0.26 accepts the setting but drops it during conversion. Check
        # the resolved settings first, including callback/add_typer overrides.
        resolved = solve_typer_info_defaults(info)
        if resolved.chain:
            raise IntrospectionError(
                "chain=True is unsupported by the Typer 0.26 parser; "
                "cannot generate chained-command completions"
            )
        for child in info.typer_instance.registered_groups:
            reject_chain(child)

    try:
        reject_chain(TyperInfo(app))
        command = get_command(app)
    except IntrospectionError:
        raise
    except Exception as exc:
        raise IntrospectionError(f"Cannot read Typer app: {exc}") from exc
    return from_command(
        command,
        prog_name,
        include_hidden=include_hidden,
        include_deprecated=include_deprecated,
        max_depth=max_depth,
    )


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
    if not prog_name or any(ord(c) < 32 for c in prog_name):
        raise IntrospectionError(
            "Program name must be nonempty and contain no controls"
        )
    if max_depth is not None and max_depth < 0:
        raise IntrospectionError("max_depth must be nonnegative")

    def retained(obj: Any) -> bool:
        return (include_hidden or not getattr(obj, "hidden", False)) and (
            include_deprecated or not getattr(obj, "deprecated", False)
        )

    def visit(cmd: Any, path: tuple[str, ...], parent: Any = None) -> Command:
        if not hasattr(cmd, "params") or not hasattr(cmd, "context_class"):
            raise IntrospectionError("Expected a Typer command")
        ctx = cmd.context_class(
            cmd,
            info_name=path[-1] if path else prog_name,
            parent=parent,
            resilient_parsing=True,
            **(cmd.context_settings or {}),
        )
        if ctx.token_normalize_func or ctx.ignore_unknown_options:
            raise IntrospectionError(
                "Token normalization and unknown-option passthrough are not supported yet"
            )
        is_group = hasattr(cmd, "commands")
        if is_group and ctx.allow_interspersed_args:
            raise IntrospectionError("Interspersed group options are not supported yet")
        if not is_group and not ctx.allow_interspersed_args:
            raise IntrospectionError(
                "Non-interspersed leaf options are not supported yet"
            )
        help_option = cmd.get_help_option(ctx)
        params = []
        for p in cmd.get_params(ctx):
            if not retained(p):
                continue
            kind = ParamKind(p.param_type_name)

            def describe(type_: Any) -> ValueSpec:
                value_kind = ValueKind.OPAQUE
                if getattr(p, "is_flag", False) or getattr(p, "count", False):
                    value_kind = ValueKind.FLAG
                elif getattr(p, "_custom_shell_complete", None):
                    value_kind = ValueKind.DYNAMIC
                elif hasattr(type_, "choices"):
                    value_kind = ValueKind.CHOICE
                elif type_.name in DIRECTORY_TYPE_NAMES or (
                    type_.name == "path" and not type_.file_okay
                ):
                    value_kind = ValueKind.DIRECTORY
                elif type_.name in FILE_TYPE_NAMES:
                    value_kind = ValueKind.FILE
                return ValueSpec(
                    value_kind,
                    tuple(
                        str(getattr(c, "value", c))
                        for c in getattr(type_, "choices", ())
                    ),
                    case_sensitive=getattr(type_, "case_sensitive", True),
                )

            value = describe(p.type)
            values = tuple(describe(t) for t in getattr(p.type, "types", ()))
            flags = tuple(p.opts + p.secondary_opts)
            if p is help_option:
                # Typer deduplicates help aliases with a set. Restore the user's
                # configured order so output does not depend on Python's hash seed.
                configured = [flag for flag in ctx.help_option_names if flag in flags]
                flags = tuple(
                    dict.fromkeys(configured + sorted(set(flags) - set(configured)))
                )
            params.append(
                Param(
                    kind=kind,
                    name=p.name or "",
                    value_kind=value.value_kind,
                    flags=flags if kind is ParamKind.OPTION else (),
                    negation_flags=tuple(p.secondary_opts)
                    if kind is ParamKind.OPTION
                    else (),
                    choices=value.choices,
                    values=values,
                    case_sensitive=value.case_sensitive,
                    help=(getattr(p, "help", None) or "").split("\n")[0].strip(),
                    metavar=p.metavar,
                    required=p.required,
                    nargs=p.nargs,
                    multiple=getattr(p, "multiple", False)
                    or getattr(p, "count", False),
                    hidden=getattr(p, "hidden", False),
                    deprecated=bool(getattr(p, "deprecated", False)),
                    is_help=p is help_option,
                )
            )
        children = {}
        if max_depth is None or len(path) < max_depth:
            children = {
                name: visit(child, (*path, name), ctx)
                for name, child in getattr(cmd, "commands", {}).items()
                if retained(child)
            }
        return Command(
            path=path,
            help=(cmd.help or "").split("\n")[0].strip(),
            params=tuple(params),
            subcommands=children,
            is_group=is_group,
            hidden=cmd.hidden,
            deprecated=bool(cmd.deprecated),
            chain=getattr(cmd, "chain", False),
        )

    try:
        return CommandTree(prog_name=prog_name, root=visit(command, ()))
    except IntrospectionError:
        raise
    except Exception as exc:
        raise IntrospectionError(f"Cannot read command tree: {exc}") from exc


def load_app(target: str) -> typer.Typer:
    """Import a ``"module:attribute"`` target and return the app.

    Also accepts a bare ``"module"``, in which case a module-level ``app``,
    ``cli`` or ``main`` attribute is used, in that order.

    Note that this *imports the target module*, running its side effects, in the
    current interpreter. For an app that is expensive or unsafe to import in the
    build environment, generate in a subprocess instead.

    Raises:
        AppLoadError: if the import fails, the attribute is missing, or the
            object is not a ``Typer`` app. Wrapper functions and factories are never
            called; pass an explicit app instance to generate() or write() instead.
    """
    import importlib

    import typer

    from .errors import AppLoadError

    module_name, separator, attribute = target.partition(":")
    try:
        module = importlib.import_module(module_name)
        if separator:
            obj: Any = module
            for part in attribute.split("."):
                obj = getattr(obj, part)
        else:
            obj = next(
                (
                    getattr(module, name)
                    for name in ("app", "cli", "main")
                    if isinstance(getattr(module, name, None), typer.Typer)
                ),
                None,
            )
        if not isinstance(obj, typer.Typer):
            raise TypeError(
                "Target must be a Typer instance; wrappers and factories are not called"
            )
        return obj
    except (Exception, SystemExit) as exc:
        raise AppLoadError(f"Cannot load {target!r}: {exc}") from exc
