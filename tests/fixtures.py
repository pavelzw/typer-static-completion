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


class RootTarget(str, Enum):
    root = "root"
    remote = "remote"


class GroupTarget(str, Enum):
    group = "group"
    green = "green"


def parsing_fixture() -> typer.Typer:
    """Options shadow each other across scopes; values can look like commands."""
    app = typer.Typer(add_completion=False)
    remote = typer.Typer()

    @app.callback()
    def root(
        target: RootTarget = typer.Option(RootTarget.root, "--target", "-t"),
        token: str = typer.Option("", "--token", "-k"),
        verbose: int = typer.Option(0, "--verbose", "-v", count=True),
        root_only: bool = False,
    ):
        pass

    @remote.callback()
    def group(target: GroupTarget = typer.Option(GroupTarget.group, "--target", "-t")):
        pass

    def paint(
        first: Color,
        rest: list[Color] = typer.Argument(None),
        target: Color = typer.Option(Color.red, "--target", "-t"),
        color: Color = typer.Option(Color.red, "--color", "-c"),
        tag: list[Color] = typer.Option(None, "--tag", "-g"),
        token: str = typer.Option("", "--token", "-k"),
        verbose: int = typer.Option(0, "--verbose", "-v", count=True),
        quiet: bool = typer.Option(False, "--quiet", "-q"),
    ):
        """Paint one or more colors."""

    app.command()(paint)
    remote.command()(paint)
    app.add_typer(remote, name="remote")
    return app


class Literal(str, Enum):
    apostrophe = "apos'trophe"
    unicode = "café"
    brackets = "bracket[one]:two"
    dollar = "dollar$(demo)"
    backtick = "tick`demo`"
    double_quote = 'quote"double'
    backslash = "slash\\path"


def coverage_fixture() -> typer.Typer:
    """Help configuration, visibility, and literal values in one shared tree."""
    app = typer.Typer(
        add_completion=False, context_settings={"help_option_names": ["-h", "--assist"]}
    )

    @app.command(context_settings={"help_option_names": ["-h", "--assist"]})
    def show(
        value: Literal = typer.Option(
            Literal.unicode, help='Use [x]: "$HOME", `demo`, and $(demo).'
        ),
        secret: bool = typer.Option(False, hidden=True),
    ):
        """Show literal values: [x], $HOME, and `demo`."""

    @app.command(name="internal-secret", hidden=True)
    def hidden():
        """A hidden command."""

    @app.command(name="legacy-deprecated", deprecated=True)
    def legacy():
        """A deprecated command."""

    @app.command(context_settings={"help_option_names": []})
    def bare():
        """A command without a help flag."""

    return app


def tuple_fixture() -> typer.Typer:
    """Heterogeneous tuple options at parent and leaf scope."""
    app = typer.Typer(add_completion=False)

    @app.callback()
    def root(pair: tuple[str, str] = typer.Option(None, "--pair")):
        pass

    @app.command()
    def paint(
        pair: tuple[Color, GroupTarget] = typer.Option(None, "--pair", "-p"),
        resource: tuple[Color, Path] = typer.Option(None, "--resource"),
        triple: tuple[str, str, Color] = typer.Option(None, "--triple"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ):
        typer.echo(repr(pair))

    return app
