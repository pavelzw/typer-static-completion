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
    #: Failed imports also make the check fail, even if existing files match.
    skipped: Mapping[str, str] = field(default_factory=dict)
    #: Unmanaged destinations or edited orphans that sync refuses to replace/delete.
    conflicts: Mapping[Path, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return not (
            self.stale
            or self.missing
            or self.orphaned
            or self.skipped
            or self.conflicts
        )

    def __bool__(self) -> bool:
        return self.ok

    def report(self, *, max_files: int = 5, show_diffs: bool = True) -> str:
        """A human-readable summary; show at most max_files details and 80 diff lines per file."""
        if max_files < 0:
            raise ValueError("max_files must be nonnegative")
        if self.ok:
            return "Completions are up to date."
        lines = [
            f"Completions: {len(self.stale)} stale, {len(self.missing)} missing, "
            f"{len(self.orphaned)} orphaned, {len(self.skipped)} skipped, "
            f"{len(self.conflicts)} conflicts."
        ]
        details = [
            (f"{label}: {path}", self.diffs.get(path, "") if show_diffs else "")
            for label, paths in (
                ("stale", self.stale),
                ("missing", self.missing),
                ("orphaned", self.orphaned),
            )
            for path in paths
        ]
        details.extend(
            (f"skipped: {name}: {reason}", "")
            for name, reason in sorted(self.skipped.items())
        )
        details.extend(
            (f"conflict: {path}: {reason}", "")
            for path, reason in sorted(self.conflicts.items())
        )
        for message, diff in details[:max_files]:
            lines.append(message[:1000])
            if diff:
                diff_lines = diff.splitlines()
                lines.extend(line[:1000] for line in diff_lines[:80])
                if len(diff_lines) > 80:
                    lines.append("... diff truncated")
        if len(details) > max_files:
            lines.append(f"... {len(details) - max_files} more entries")
        return "\n".join(lines)

    def raise_for_status(self) -> None:
        """Raise :exc:`~typer_static_completions.errors.StaleCompletionsError`
        unless everything is up to date."""
        from .errors import StaleCompletionsError

        if not self.ok:
            raise StaleCompletionsError(self.report())


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
        """Summarize writes and at most five import failures."""
        lines = [
            f"Completions: {len(self.written)} written, {len(self.unchanged)} unchanged, {len(self.removed)} removed, {len(self.skipped)} skipped."
        ]
        lines.extend(
            f"skipped: {name}: {reason}"[:1000]
            for name, reason in sorted(self.skipped.items())[:5]
        )
        if len(self.skipped) > 5:
            lines.append(f"... {len(self.skipped) - 5} more skipped")
        return "\n".join(lines)


class CompletionSet:
    """A group of apps whose completion scripts are managed together.

    The unit of the build-time workflow: generate every script for every app,
    verify committed copies are current, and delete ones that no longer belong.

    Example:
        >>> from myapp.cli import app
        >>> completions = CompletionSet(
        ...     {"myapp": app}, output_dir="completions",
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
        from .generators import get_generator

        self._only_owners: frozenset[str] | None = None
        self.apps = dict(apps)
        self.output_dir = Path(output_dir)
        self.shells = tuple(dict.fromkeys(DEFAULT_SHELLS if shells is None else shells))
        self.options = options or GenerationOptions()
        self.layout = dict(layout or {})
        for shell in self.shells:
            get_generator(shell, self.options)
        for name, app in self.apps.items():
            if not name or any(ord(char) < 32 for char in name):
                raise ValueError(
                    "Program names must be nonempty and contain no controls"
                )
            if isinstance(app, CommandTree) and app.prog_name != name:
                raise ValueError(f"Tree program name must match mapping key {name!r}")

    @classmethod
    def from_pyproject(
        cls,
        pyproject: Path | str | None = None,
        *,
        output_dir: Path | str,
        only: Sequence[str] | None = None,
        overrides: Mapping[str, typer.Typer | CommandTree | str] | None = None,
        shells: Iterable[ShellName] | None = None,
        options: GenerationOptions | None = None,
        layout: Mapping[ShellName, str] | None = None,
    ) -> CompletionSet:
        """Build a set from ``[project.scripts]`` without importing its targets.

        Args:
            pyproject: Defaults to the nearest ``pyproject.toml`` at or above the
                current directory.
            only: Limit to these console script names. Sync/check preserve all
                previously owned outputs outside this selection, even if their
                entrypoints have since been removed. An empty selection manages
                no scripts. Omit to manage the whole project, including removals.
            overrides: Replace declared script targets with Typer instances,
                CommandTrees, or import strings pointing to apps rather than
                wrappers. Keys must exist in the project's scripts table;
                overrides outside ``only`` are validated but not loaded.
            output_dir: Relative paths remain relative to the current working
                directory, as in the constructor, not to the pyproject file.

        Raises:
            AppLoadError: if the file is unreadable, has no ``[project.scripts]``,
                or ``only``/``overrides`` names a script that is not there.

        Targets must already be importable in the current environment. This method
        does not change cwd/sys.path or call wrapper functions/factories.
        """
        from .errors import AppLoadError
        from .introspect import entrypoints

        scripts = entrypoints(pyproject)
        selected = set(scripts) if only is None else set(only)
        replacements = dict(overrides or {})
        unknown = (selected | replacements.keys()) - scripts.keys()
        if unknown:
            raise AppLoadError("Unknown console scripts: " + ", ".join(sorted(unknown)))
        apps: dict[str, typer.Typer | CommandTree | str] = {
            name: replacements.get(name, scripts[name]) for name in sorted(selected)
        }
        result = cls(
            apps, output_dir=output_dir, shells=shells, options=options, layout=layout
        )
        if only is not None:
            result._only_owners = frozenset(selected)
        return result

    def _trees(self) -> tuple[dict[str, CommandTree], dict[str, str]]:
        from .errors import AppLoadError
        from .introspect import load_app

        trees: dict[str, CommandTree] = {}
        skipped: dict[str, str] = {}
        for name, app in sorted(self.apps.items()):
            try:
                loaded = load_app(app) if isinstance(app, str) else app
            except AppLoadError as exc:
                skipped[name] = str(exc)
                continue
            trees[name] = _tree(
                loaded, None if isinstance(loaded, CommandTree) else name, self.options
            )
        return trees, skipped

    def _render(self) -> tuple[dict[Path, str], dict[Path, str], dict[str, str]]:
        trees, skipped = self._trees()
        outputs: dict[Path, str] = {}
        owners: dict[Path, str] = {}
        for name, tree in trees.items():
            for path, content in write(
                tree,
                output_dir=self.output_dir,
                shells=self.shells,
                options=self.options,
                layout=self.layout,
                dry_run=True,
            ).items():
                resolved = path.resolve()
                if any(
                    resolved == other.resolve()
                    or resolved in other.resolve().parents
                    or other.resolve() in resolved.parents
                    for other in outputs
                ):
                    raise ValueError(f"Completion layout collision: {path}")
                outputs[path] = content
                owners[path] = name
        return outputs, owners, skipped

    def render(self) -> dict[Path, str]:
        """Render scripts without writes; raise AppLoadError on any failed import.

        Use sync/check for partial results with explicit skipped-app diagnostics.
        Ownership metadata is not included in this mapping.
        """
        from .errors import AppLoadError

        outputs, _, skipped = self._render()
        if skipped:
            raise AppLoadError(
                "; ".join(f"{name}: {reason}" for name, reason in skipped.items())
            )
        return outputs

    def sync(self, *, prune: bool = True) -> SyncResult:
        """Write scripts and ownership metadata, optionally deleting owned orphans.

        Only files recorded by a previous sync can be pruned. Failed imports
        retain their previous files. Unmanaged files with differing content and
        edited orphans raise ValueError before any writes. Matching unmanaged
        scripts can be adopted (for example, outputs from write()).
        Replacements are atomic per file, not across the set. Use one manager
        per output directory; concurrent syncs are not supported.
        """
        from ._management import MANIFEST, prepare

        outputs, owners, skipped = self._render()
        plan = prepare(
            self.output_dir,
            outputs,
            owners,
            skipped,
            prune=prune,
            only_owners=self._only_owners,
        )
        if plan.conflicts:
            raise ValueError(
                "Completion ownership conflicts: "
                + "; ".join(
                    f"{path}: {reason}" for path, reason in plan.conflicts.items()
                )
            )
        written: list[Path] = []
        unchanged: list[Path] = []

        def update(path: Path, content: bytes) -> None:
            if path.exists() and path.read_bytes() == content:
                unchanged.append(path)
            else:
                _replace_file(path, content)
                written.append(path)

        manifest = self.output_dir / MANIFEST
        for path, content in plan.outputs.items():
            if path != manifest:
                update(path, content)
        for path in plan.orphaned:
            path.unlink()
        # Publish ownership last: failed writes/deletions remain recoverable.
        update(manifest, plan.outputs[manifest])
        return SyncResult(tuple(written), tuple(unchanged), plan.orphaned, skipped)

    def check(self, *, prune: bool = True, diffs: bool = True) -> CheckResult:
        """Compare scripts and ownership metadata without writing.

        Failed imports make the result falsy and preserve that app's ownership.
        prune=False ignores old outputs while retaining them for future pruning.
        Diffs use UTF-8 with replacement for undecodable existing content.
        """
        import difflib

        from ._management import prepare

        outputs, owners, skipped = self._render()
        plan = prepare(
            self.output_dir,
            outputs,
            owners,
            skipped,
            prune=prune,
            only_owners=self._only_owners,
        )
        stale: list[Path] = []
        missing: list[Path] = []
        changes: dict[Path, str] = {}
        for path, content in plan.outputs.items():
            if not path.exists():
                missing.append(path)
                continue
            current = path.read_bytes()
            if current != content:
                stale.append(path)
                if diffs:
                    lines = difflib.unified_diff(
                        current.decode("utf-8", errors="replace").splitlines(
                            keepends=True
                        ),
                        content.decode("utf-8").splitlines(keepends=True),
                        fromfile=str(path),
                        tofile=str(path) + " (generated)",
                    )
                    changes[path] = "".join(
                        line
                        if line.endswith("\n")
                        else line + "\n\\ No newline at end of file\n"
                        for line in lines
                    )

        return CheckResult(
            tuple(stale),
            tuple(missing),
            plan.orphaned,
            changes,
            skipped,
            plan.conflicts,
        )

    def trees(self) -> dict[str, CommandTree]:
        """Introspect every app; raise AppLoadError rather than silently omitting failures."""
        from .errors import AppLoadError

        trees, skipped = self._trees()
        if skipped:
            raise AppLoadError(
                "; ".join(f"{name}: {reason}" for name, reason in skipped.items())
            )
        return trees
