"""Ground completion expectations in Typer's actual parser and extracted metadata."""

import pytest
from fixtures import parsing_fixture
from typer.testing import CliRunner

from typer_static_completion import ValueKind, from_app


def test_parsing_metadata():
    tree = from_app(parsing_fixture(), "demo")
    paint = tree.find(["paint"])
    assert paint is not None
    assert [(p.name, p.nargs) for p in paint.arguments] == [("first", 1), ("rest", -1)]
    options = {p.name: p for p in paint.options}
    assert options["tag"].multiple
    assert options["tag"].flags == ("--tag", "-g")
    assert options["verbose"].multiple
    assert options["verbose"].value_kind is ValueKind.FLAG
    targets = []
    for path in ([], ["remote"], ["remote", "paint"]):
        command = tree.find(path)
        assert command is not None
        targets.append(next(p.choices for p in command.options if p.name == "target"))
    assert targets[0] == ("root", "remote")
    assert targets[1] == ("group", "green")
    assert "blue" in targets[2]


@pytest.mark.parametrize(
    "line,exit_code",
    [
        ("paint red blue rose", 0),
        ("paint red --tag blue rose", 0),
        ("paint --tag red --tag blue red", 0),
        ("paint -qvcred blue", 0),
        ("paint -qvc red blue", 0),
        ("paint -vvvq blue", 0),
        ("-vkremote paint blue", 0),
        ("paint -- blue", 0),
        ("paint --token -- --color red blue", 0),
        ("paint --token --tag blue", 0),
        ("-- remote --target green paint blue", 0),
        ("remote -- paint --target blue red", 0),
        ("remote paint --root-only red", 2),
        ("unknown remote paint blue", 2),
        ("remote unknown paint blue", 2),
    ],
)
def test_typer_parser_contract(line, exit_code):
    result = CliRunner().invoke(parsing_fixture(), line.split())
    assert result.exit_code == exit_code, result.output
