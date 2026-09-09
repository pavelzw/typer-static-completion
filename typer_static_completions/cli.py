"""Build-time command line interface, itself a statically completable Typer app."""

from __future__ import annotations

import contextlib
import sys
from enum import StrEnum
from pathlib import Path
from typing import Annotated

import typer

from .core import _replace_file, generate
from .errors import StaticCompletionError
from .introspect import load_app


class CompletionShell(StrEnum):
    """Shells implemented by the CLI."""

    bash = "bash"
    fish = "fish"
    zsh = "zsh"


def build_cli() -> typer.Typer:
    """Construct the generate command with no dynamic completion hooks."""
    cli = typer.Typer(
        add_completion=False,
        help="Generate static shell completions.",
        pretty_exceptions_enable=False,
    )

    @cli.callback()
    def root() -> None:
        """Generate static shell completions."""

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

    return cli


app = build_cli()


def main(argv: list[str] | None = None) -> int:
    """Run the CLI: 0 success, 2 usage or operation error."""
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


if __name__ == "__main__":
    raise SystemExit(main())
