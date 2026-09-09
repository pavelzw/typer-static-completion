"""Try: pixi run example deploy --environment staging."""

from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(add_completion=False, help="A small deployment CLI.")


class Environment(str, Enum):
    development = "development"
    staging = "staging"
    production = "production"


@app.command()
def deploy(
    environment: Annotated[
        Environment, typer.Option(help="Deployment environment.")
    ] = Environment.development,
    config: Annotated[Path, typer.Option(help="Configuration file.")] = Path(
        "deploy.toml"
    ),
):
    """Show the requested deployment."""
    typer.echo(f"Deploy to {environment.value} using {config}")


@app.command()
def status():
    """Show deployment status."""
    typer.echo("Ready")


if __name__ == "__main__":
    app(prog_name="shipyard")
