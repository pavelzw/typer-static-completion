"""Generate a script in memory or write one app's scripts to a directory."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import TYPE_CHECKING

from .config import GenerationOptions
from .model import CommandTree
from .shells import DEFAULT_SHELLS, ShellName

if TYPE_CHECKING:
    import typer


def generate(
    app: typer.Typer | CommandTree,
    prog_name: str | None = None,
    shell: ShellName = "bash",
    *,
    options: GenerationOptions | None = None,
) -> str:
    """Render a static completion script and return it.

    The one function most callers need. Pure: no files are touched.

    Args:
        app: A ``Typer`` app, or an already-introspected
            :class:`~typer_static_completion.model.CommandTree`.
        prog_name: The name users type. Required for a ``Typer`` app; ignored
            (and must be ``None``) when a tree is passed, which already has one.
        shell: Target shell.
        options: Content settings. Defaults to
            :class:`~typer_static_completion.config.GenerationOptions`.

    Raises:
        UnsupportedShellError: if no generator is registered for ``shell``.
        IntrospectionError: if the app's command tree cannot be read.

    Example:
        >>> from myapp.cli import app
        >>> script = generate(app, "myapp", "fish")
    """
    from .generators import get_generator

    settings = options or GenerationOptions()
    generator = get_generator(shell, settings)
    return generator.render(_tree(app, prog_name, settings))


def _tree(
    app: typer.Typer | CommandTree,
    prog_name: str | None,
    settings: GenerationOptions,
) -> CommandTree:
    from .introspect import from_app

    if isinstance(app, CommandTree):
        if prog_name is not None:
            raise ValueError("prog_name must be omitted for a CommandTree")
        return app
    if not prog_name:
        raise ValueError("prog_name is required for a Typer app")
    return from_app(
        app,
        prog_name,
        include_hidden=settings.include_hidden,
        include_deprecated=settings.include_deprecated,
    )


def write(
    app: typer.Typer | CommandTree,
    prog_name: str | None = None,
    *,
    output_dir: Path | str,
    shells: Iterable[ShellName] | None = None,
    options: GenerationOptions | None = None,
    layout: Mapping[ShellName, str] | None = None,
    dry_run: bool = False,
) -> dict[Path, str]:
    """Generate for several shells and write them out.

    Args:
        output_dir: Root for the written files. Created if absent.
        shells: Defaults to :data:`~typer_static_completion.shells.DEFAULT_SHELLS`.
        layout: Override the per-shell path template, e.g. to write directly into
            a prefix with ``{"bash": "share/bash-completion/completions/{prog}"}``.
            Defaults to each generator's ``filename`` in a per-shell subdirectory.
        dry_run: Compute the mapping without writing. Useful for previewing.

    Returns:
        ``{path: content}`` for all selected outputs, including unchanged files.
        Paths retain the relative/absolute form of ``output_dir``.

    Unchanged files retain their modification times. All scripts and destinations
    are validated before writing. Each changed file is replaced atomically as
    UTF-8 with LF newlines; an I/O failure can still leave a partially updated set.
    Existing file permissions are retained; new files use mode 0644.
    Layouts must stay beneath ``output_dir``, contain no symlinks beneath that
    root, and must not collide. Invalid destinations raise ``ValueError`` or an
    ``OSError``. A dry run performs the same validation without creating files.
    """
    from .generators import get_generator

    settings = options or GenerationOptions()
    tree = _tree(app, prog_name, settings)
    root = Path(output_dir)
    rendered: dict[Path, str] = {}
    destinations: set[Path] = set()
    for shell in dict.fromkeys(DEFAULT_SHELLS if shells is None else shells):
        generator = get_generator(shell, settings)
        template = (layout or {}).get(shell, generator.shell + "/" + generator.filename)
        path = _output_path(root, template.format(prog=tree.prog_name))
        destination = path.resolve()
        if any(
            destination == other
            or destination in other.parents
            or other in destination.parents
            for other in destinations
        ):
            raise ValueError(f"Completion layout collision: {path}")
        destinations.add(destination)
        rendered[path] = generator.render(tree)

    # Render and inspect every destination before making any filesystem changes.
    changed: dict[Path, bytes] = {}
    for path, content in rendered.items():
        for parent in path.parents:
            if parent.exists() and not parent.is_dir():
                raise NotADirectoryError(parent)
        data = content.encode("utf-8")
        if not path.exists() or path.read_bytes() != data:
            changed[path] = data
    if not dry_run:
        for path, data in changed.items():
            _replace_file(path, data)
    return rendered


def _output_path(root: Path, name: str) -> Path:
    """Validate a destination without creating its parents."""
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts or relative == Path("."):
        raise ValueError(f"Completion layout must be a relative file path: {relative}")
    path = root / relative
    destination = path.resolve()
    resolved_root = root.resolve()
    if not destination.is_relative_to(resolved_root) or destination == resolved_root:
        raise ValueError(f"Completion path escapes output_dir: {path}")
    if any((root / part).is_symlink() for part in (relative, *relative.parents)):
        raise ValueError(f"Completion path must not contain symlinks: {path}")
    return path


def _replace_file(path: Path, data: bytes) -> None:
    """Replace one file atomically; a set of files is not a transaction."""
    import os
    import stat
    import tempfile

    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o644
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        temporary.chmod(mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
