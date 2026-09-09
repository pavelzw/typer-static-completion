"""Command line interface: ``typer-static-completions``.

Wraps :mod:`typer_static_completions.core` so completions can be generated from
a build script or CI step without writing Python. Itself a Typer app, and its own
completions are generated with this library.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import typer


def build_cli() -> typer.Typer:
    """Construct the CLI app.

    A factory rather than a module-level singleton so importing this module stays
    free of side effects, and so tests can build a fresh app per case.

    Commands:
        ``generate``  Render one app's script to stdout or a file.
        ``sync``      Write every script for a whole project.
        ``check``     Exit non-zero if committed scripts are stale.
        ``install``   Write scripts into the shells' own directories.
        ``verify``    Syntax-check, and optionally complete a sample line.
    """
    raise NotImplementedError


def main(argv: list[str] | None = None) -> int:
    """Entry point for the ``typer-static-completions`` console script.

    Returns a process exit status rather than raising, so it is usable as a
    library call too: ``0`` ok, ``1`` stale (from ``check``), ``2`` usage error.
    """
    raise NotImplementedError


def _default_output_dir(pyproject: Path | None = None) -> Path:
    """``completions/`` beside the nearest ``pyproject.toml``."""
    raise NotImplementedError


if __name__ == "__main__":
    raise SystemExit(main())
