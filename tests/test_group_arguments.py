import shlex

import pytest
import typer
from fixtures import group_argument_fixture
from typer.testing import CliRunner

from typer_static_completion import IntrospectionError, from_app


@pytest.mark.parametrize(
    "line,exit_code",
    [
        ("root deploy blue", 0),
        ('root optional "" show', 0),
        ('root files "nested directory" show', 0),
        ("remote remote blue green paint blue", 0),
        ("--profile=red root deploy blue", 0),
        ("-pred root deploy blue", 0),
        ("-- root deploy --mode red blue", 0),
        ("root remote --mode red blue green paint blue", 0),
        ("root remote -- blue green paint --mode bLue blue", 0),
        ("root optional show show", 0),
        ("root optional show", 2),
        ("root --profile red deploy blue", 2),
        ("root remote blue --mode red green paint blue", 2),
        ("root remote blue -- green paint blue", 2),
        ("root many blue rose", 0),
        ("root many blue show", 2),
        ("root unknown remote blue green paint blue", 2),
    ],
)
def test_group_parser_contract(line, exit_code):
    result = CliRunner().invoke(group_argument_fixture(), shlex.split(line))
    assert result.exit_code == exit_code, result.output


def test_group_metadata():
    tree = from_app(group_argument_fixture(), "demo")
    assert tree.root.arguments[0].name == "workspace"
    remote = tree.find(["remote"])
    assert remote is not None
    assert remote.arguments[0].nargs == 2
    optional = tree.find(["optional"])
    assert optional is not None
    assert not optional.arguments[0].required


def test_interspersed_groups_are_diagnosed():
    app = typer.Typer(context_settings={"allow_interspersed_args": True})

    @app.callback()
    def root(workspace: str):
        pass

    @app.command()
    def deploy():
        pass

    with pytest.raises(IntrospectionError, match="Interspersed group options"):
        from_app(app, "demo")
