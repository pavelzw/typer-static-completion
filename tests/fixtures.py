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


class MixedCase(str, Enum):
    blue = "Blue"
    red = "RED"
    rose = "Rose"
    spaced = "Two Words"
    accent = "Café"


def case_fixture() -> typer.Typer:
    app = typer.Typer(add_completion=False)

    @app.command()
    def paint(
        color: MixedCase = typer.Argument(MixedCase.blue, case_sensitive=False),
        mode: MixedCase = typer.Option(
            MixedCase.blue, "--mode", "-m", case_sensitive=False
        ),
        strict: MixedCase = typer.Option(MixedCase.blue),
        pair: tuple[MixedCase, MixedCase] = typer.Option(None, case_sensitive=False),
    ):
        typer.echo(color.value + ":" + mode.value)

    return app


def tuple_argument_fixture() -> typer.Typer:
    app = typer.Typer(add_completion=False)

    @app.command()
    def paint(
        pair: tuple[Color, GroupTarget],
        rest: list[Color] = typer.Argument(None),
        mode: Color = typer.Option(Color.red, "--mode", "-m"),
        verbose: bool = typer.Option(False, "--verbose", "-v"),
    ):
        typer.echo(repr((pair, rest, mode)))

    @app.command()
    def framed(first: RootTarget, pair: tuple[Color, GroupTarget], last: MixedCase):
        pass

    @app.command()
    def resource(pair: tuple[Color, Path]):
        pass

    @app.command()
    def directory(pair: tuple[Color, Path] = typer.Argument(..., file_okay=False)):
        pass

    @app.command()
    def triple(
        values: tuple[str, str, MixedCase] = typer.Argument(..., case_sensitive=False),
    ):
        pass

    return app


def group_argument_fixture() -> typer.Typer:
    app = typer.Typer(add_completion=False)
    remote = typer.Typer()
    files = typer.Typer()
    optional = typer.Typer()
    many = typer.Typer(invoke_without_command=True)

    @app.callback()
    def root(
        workspace: RootTarget,
        profile: Color = typer.Option(Color.red, "--profile", "-p"),
    ):
        pass

    @app.command()
    def deploy(color: Color, mode: Color = typer.Option(Color.red, "--mode", "-m")):
        pass

    @remote.callback()
    def remote_root(
        pair: tuple[Color, GroupTarget],
        mode: Color = typer.Option(Color.red, "--mode", "-m"),
    ):
        pass

    @remote.command()
    def paint(
        color: Color,
        mode: MixedCase = typer.Option(
            MixedCase.blue, "--mode", "-m", case_sensitive=False
        ),
    ):
        pass

    @files.callback()
    def files_root(directory: Path = typer.Argument(..., file_okay=False)):
        pass

    @files.command("show")
    def files_show():
        pass

    @optional.callback()
    def optional_root(label: str = typer.Argument("default")):
        pass

    @optional.command("show")
    def optional_show():
        pass

    @many.callback()
    def many_root(colors: list[Color] = typer.Argument(None)):
        pass

    @many.command("show")
    def many_show():
        pass

    app.add_typer(remote, name="remote")
    app.add_typer(files, name="files")
    app.add_typer(optional, name="optional")
    app.add_typer(many, name="many")
    return app


class UnicodeValue(str, Enum):
    tokyo = "東京"
    osaka = "大阪"
    rocket = "🚀launch"
    decomposed = "cafe\u0301"
    combining = "a\u0308\u0301value"


def unicode_fixture() -> typer.Typer:
    app = typer.Typer(add_completion=False)

    @app.command()
    def show(
        value: UnicodeValue = typer.Option(UnicodeValue.tokyo, "--value", "-v"),
        quiet: bool = False,
    ):
        typer.echo(value.value)

    return app
