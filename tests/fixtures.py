"""Shared Typer app for generator and interactive behavior tests."""

from enum import Enum
from pathlib import Path

import typer


class Color(str, Enum):
    red = "red"
    rose = "rose"
    blue = "blue"
    two_words = "two words"
    apostrophe = "quote's"


def fixture() -> typer.Typer:
    app = typer.Typer(add_completion=False)
    remote = typer.Typer()

    @app.callback()
    def root(profile: str = "", verbose: bool = False):
        """Demo application."""

    @app.command()
    def deploy(
        color: Color = typer.Option(Color.red, "--color", "-c"),
        config: Path = typer.Option(Path("."), "--config"),
        directory: Path = typer.Option(Path("."), "--directory", file_okay=False),
        cache: bool = typer.Option(True, "--cache/--no-cache"),
    ):
        """Deploy an application."""

    @app.command()
    def tasks():
        """List tasks."""

    @app.command()
    def tags():
        """List tags."""

    @remote.command()
    def add(name: str):
        """Add a remote."""

    @remote.command()
    def remove(name: str):
        """Remove a remote."""

    app.add_typer(remote, name="remote")
    return app
