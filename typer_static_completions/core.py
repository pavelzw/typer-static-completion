"""The primary API.

Three layers, so a caller only meets the complexity they need:

1. :func:`generate` -- one app, one shell, returns a string. No filesystem.
2. :func:`write` -- one app, several shells, to a directory.
3. :class:`CompletionSet` -- many apps (a whole ``[project.scripts]`` table),
   with staleness checking and orphan pruning.

Layer 3 exists because the interesting operations are set-level: a renamed
entrypoint leaves an orphaned script that keeps completing a command that no
longer exists, and that is invisible to any per-app function.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
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
            :class:`~typer_static_completions.model.CommandTree`.
        prog_name: The name users type. Required for a ``Typer`` app; ignored
            (and must be ``None``) when a tree is passed, which already has one.
        shell: Target shell.
        options: Content settings. Defaults to
            :class:`~typer_static_completions.config.GenerationOptions`.

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
        shells: Defaults to :data:`~typer_static_completions.shells.DEFAULT_SHELLS`.
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
    resolved_root = root.resolve()
    rendered: dict[Path, str] = {}
    destinations: set[Path] = set()
    for shell in dict.fromkeys(DEFAULT_SHELLS if shells is None else shells):
        generator = get_generator(shell, settings)
        template = (layout or {}).get(shell, generator.shell + "/" + generator.filename)
        relative = Path(template.format(prog=tree.prog_name))
        if relative.is_absolute() or ".." in relative.parts or relative == Path("."):
            raise ValueError(
                f"Completion layout must be a relative file path: {relative}"
            )
        path = root / relative
        destination = path.resolve()
        if (
            not destination.is_relative_to(resolved_root)
            or destination == resolved_root
        ):
            raise ValueError(f"Completion path escapes output_dir: {path}")
        if any((root / part).is_symlink() for part in (relative, *relative.parents)):
            raise ValueError(f"Completion path must not contain symlinks: {path}")
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


@dataclass(frozen=True)
class CheckResult:
    """Outcome of :meth:`CompletionSet.check`.

    Falsy when anything is out of date, so ``if not result:`` reads naturally.
    """

    #: Files whose content differs from what the app produces now.
    stale: tuple[Path, ...] = ()
    #: Files that should exist but do not.
    missing: tuple[Path, ...] = ()
    #: Files present under a managed directory with no corresponding entrypoint,
    #: usually a renamed or removed console script.
    orphaned: tuple[Path, ...] = ()
    #: Unified diffs keyed by path, for the stale files.
    diffs: Mapping[Path, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        raise NotImplementedError

    def __bool__(self) -> bool:
        raise NotImplementedError

    def report(self, *, max_files: int = 5, show_diffs: bool = True) -> str:
        """A human-readable summary suitable for stderr in CI."""
        raise NotImplementedError

    def raise_for_status(self) -> None:
        """Raise :exc:`~typer_static_completions.errors.StaleCompletionsError`
        unless everything is up to date."""
        raise NotImplementedError


@dataclass(frozen=True)
class SyncResult:
    """Outcome of :meth:`CompletionSet.sync`."""

    written: tuple[Path, ...] = ()
    #: Files whose content was already correct and so left alone; keeps mtimes
    #: stable, which matters for build caching.
    unchanged: tuple[Path, ...] = ()
    removed: tuple[Path, ...] = ()
    #: Entrypoints that could not be imported, mapped to the reason. A broken CLI
    #: does not abort the others -- it is reported here instead.
    skipped: Mapping[str, str] = field(default_factory=dict)

    def report(self) -> str:
        raise NotImplementedError


class CompletionSet:
    """A group of apps whose completion scripts are managed together.

    The unit of the build-time workflow: generate every script for every app,
    verify committed copies are current, and delete ones that no longer belong.

    Example:
        >>> completions = CompletionSet.from_pyproject(
        ...     output_dir="completions",
        ...     options=GenerationOptions(regenerate_command="pixi run completions"),
        ... )
        >>> completions.sync()                     # write
        >>> completions.check().raise_for_status()  # verify in CI
    """

    def __init__(
        self,
        apps: Mapping[str, typer.Typer | CommandTree | str],
        *,
        output_dir: Path | str,
        shells: Iterable[ShellName] | None = None,
        options: GenerationOptions | None = None,
        layout: Mapping[ShellName, str] | None = None,
    ) -> None:
        """
        Args:
            apps: ``{prog_name: app}``. A ``str`` value is a lazily imported
                ``"module:attribute"`` target, so an app that fails to import
                only breaks its own entry.
            output_dir: Root for all generated files.
            shells: Defaults to
                :data:`~typer_static_completions.shells.DEFAULT_SHELLS`.
            layout: Per-shell path template; see :func:`write`.
        """
        raise NotImplementedError

    @classmethod
    def from_pyproject(
        cls,
        pyproject: Path | str | None = None,
        *,
        output_dir: Path | str,
        only: Sequence[str] | None = None,
        shells: Iterable[ShellName] | None = None,
        options: GenerationOptions | None = None,
        layout: Mapping[ShellName, str] | None = None,
    ) -> CompletionSet:
        """Build a set from ``[project.scripts]``.

        Args:
            pyproject: Defaults to the nearest ``pyproject.toml`` at or above the
                current directory.
            only: Limit to these console script names.

        Raises:
            AppLoadError: if the file is unreadable, has no ``[project.scripts]``,
                or ``only`` names a script that is not there.
        """
        raise NotImplementedError

    def render(self) -> dict[Path, str]:
        """Compute ``{path: content}`` for the whole set without writing.

        Skips apps that fail to import; :meth:`sync` reports those.
        """
        raise NotImplementedError

    def sync(self, *, prune: bool = True) -> SyncResult:
        """Write every script, optionally deleting orphans.

        Only the managed per-shell subdirectories are swept, so hand-written
        loader files sitting directly in ``output_dir`` are left alone.

        Args:
            prune: Delete files under managed directories that this set does not
                produce.
        """
        raise NotImplementedError

    def check(self, *, prune: bool = True, diffs: bool = True) -> CheckResult:
        """Compare committed files against freshly generated ones.

        A generated script is a snapshot: if it drifts from the app, users get
        wrong completions with no error. Run this in CI the way you would check a
        lockfile.
        """
        raise NotImplementedError

    def trees(self) -> dict[str, CommandTree]:
        """Introspect every app, keyed by program name.

        Exposed so projects can assert on the model directly -- e.g. that every
        command in the tree shows up in the generated script, so a new
        subcommand cannot be silently omitted.
        """
        raise NotImplementedError
