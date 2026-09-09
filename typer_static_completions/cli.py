"""Build-time command line interface, itself a statically completable Typer app."""

from __future__ import annotations

import contextlib
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from .core import CompletionSet, _replace_file, generate
from .errors import StaticCompletionError
from .introspect import load_app


class CompletionShell(StrEnum):
    """Shells implemented by the CLI."""

    bash = "bash"
    fish = "fish"
    zsh = "zsh"


def _overrides(values: list[str] | None) -> dict[str, str]:
    result = {}
    for value in values or []:
        name, separator, target = value.partition("=")
        if not separator or not name or not target or name in result:
            raise typer.BadParameter("Use a unique NAME=MODULE:APP for each --app")
        result[name] = target
    return result


def _set(pyproject, output_dir, shells, only, apps) -> CompletionSet:
    return CompletionSet.from_pyproject(
        pyproject,
        output_dir=output_dir
        if output_dir is not None
        else _default_output_dir(pyproject),
        shells=shells,
        only=only,
        overrides=_overrides(apps),
    )


def build_cli() -> typer.Typer:
    """Construct generate/sync/check commands with no dynamic completion hooks."""
    cli = typer.Typer(
        add_completion=False,
        help="Generate and check static shell completions.",
        pretty_exceptions_enable=False,
    )

    @cli.command("generate")
    def generate_command(
        target: Annotated[str, typer.Argument(help="Import target, MODULE:APP.")],
        prog_name: Annotated[
            str, typer.Option("--prog-name", help="Command name users type.")
        ],
        shell: Annotated[CompletionShell, typer.Option(help="Target shell.")],
        output: Annotated[
            Path | None,
            typer.Option(
                "--output", "-o", help="Output file; omit or use - for stdout."
            ),
        ] = None,
    ) -> None:
        """Render one app's completion script."""
        with contextlib.redirect_stdout(sys.stderr):
            script = generate(load_app(target), prog_name, shell)
        if output is None or output == Path("-"):
            typer.echo(script, nl=False)
        elif not output.exists() or output.read_bytes() != script.encode("utf-8"):
            _replace_file(output, script.encode("utf-8"))

    @cli.command("sync")
    def sync_command(
        pyproject: Annotated[
            Path | None,
            typer.Option(help="Project metadata; defaults to nearest pyproject.toml."),
        ] = None,
        output_dir: Annotated[
            Path | None,
            typer.Option(
                help="Output directory; defaults to completions beside pyproject."
            ),
        ] = None,
        shell: Annotated[
            list[CompletionShell] | None,
            typer.Option(help="Shell to generate; repeat to select several."),
        ] = None,
        only: Annotated[
            list[str] | None,
            typer.Option(help="Script name to manage; repeat to select several."),
        ] = None,
        app: Annotated[
            list[str] | None,
            typer.Option(help="Override a declared script: NAME=MODULE:APP."),
        ] = None,
        prune: Annotated[
            bool,
            typer.Option(
                "--prune/--no-prune", help="Remove unchanged owned orphan files."
            ),
        ] = True,
    ) -> None:
        """Write project completions and their ownership manifest."""
        with contextlib.redirect_stdout(sys.stderr):
            result = _set(pyproject, output_dir, shell, only, app).sync(prune=prune)
        typer.echo(result.report())
        if result.skipped:
            raise typer.Exit(1)

    @cli.command("check")
    def check_command(
        pyproject: Annotated[
            Path | None,
            typer.Option(help="Project metadata; defaults to nearest pyproject.toml."),
        ] = None,
        output_dir: Annotated[
            Path | None,
            typer.Option(
                help="Output directory; defaults to completions beside pyproject."
            ),
        ] = None,
        shell: Annotated[
            list[CompletionShell] | None,
            typer.Option(help="Shell to check; repeat to select several."),
        ] = None,
        only: Annotated[
            list[str] | None,
            typer.Option(help="Script name to manage; repeat to select several."),
        ] = None,
        app: Annotated[
            list[str] | None,
            typer.Option(help="Override a declared script: NAME=MODULE:APP."),
        ] = None,
        prune: Annotated[
            bool, typer.Option("--prune/--no-prune", help="Report owned orphan files.")
        ] = True,
        diff: Annotated[
            bool, typer.Option("--diff/--no-diff", help="Include unified diffs.")
        ] = True,
        max_files: Annotated[
            int, typer.Option(min=0, help="Maximum diagnostic entries to display.")
        ] = 5,
    ) -> None:
        """Fail if committed completions differ, without writing files."""
        with contextlib.redirect_stdout(sys.stderr):
            result = _set(pyproject, output_dir, shell, only, app).check(
                prune=prune, diffs=diff
            )
        typer.echo(result.report(max_files=max_files, show_diffs=diff), err=True)
        if not result:
            raise typer.Exit(1)

    return cli


app = build_cli()


def main(argv: list[str] | None = None) -> int:
    """Run the CLI: 0 success, 1 failed check/partial sync, 2 usage or operation error."""
    from typer._click.exceptions import Abort, ClickException
    from typer.main import get_command

    try:
        result = get_command(app).main(
            args=argv, prog_name="typer-static-completions", standalone_mode=False
        )
        return int(result or 0)
    except ClickException as exc:
        exc.show()
        return exc.exit_code
    except Abort:
        typer.echo("Aborted.", err=True)
        return 2
    except (StaticCompletionError, OSError, ValueError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        return 2


def _default_output_dir(pyproject: Path | None = None) -> Path:
    """Return completions/ beside the explicit or nearest pyproject.toml."""
    if pyproject is not None:
        return pyproject.parent / "completions"
    current = Path.cwd()
    for parent in (current, *current.parents):
        if (parent / "pyproject.toml").exists():
            return parent / "completions"
    return current / "completions"


if __name__ == "__main__":
    raise SystemExit(main())
