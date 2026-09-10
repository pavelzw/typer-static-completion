import pytest
from fixtures import tuple_argument_fixture
from typer.testing import CliRunner

from typer_static_completion import ValueKind, from_app


def test_tuple_argument_metadata():
    command = from_app(tuple_argument_fixture(), "demo").find(["paint"])
    assert command is not None
    pair, rest = command.arguments
    assert pair.nargs == 2 and pair.flags == ()
    assert [v.value_kind for v in pair.values] == [ValueKind.CHOICE, ValueKind.CHOICE]
    assert pair.values[1].choices == ("group", "green")
    assert rest.nargs == -1
    tree = from_app(tuple_argument_fixture(), "demo")
    directory = tree.find(["directory"])
    assert directory is not None
    assert directory.arguments[0].values[1].value_kind is ValueKind.DIRECTORY


@pytest.mark.parametrize(
    "words",
    [
        ["paint", "blue", "green"],
        ["paint", "blue", "--verbose", "green"],
        ["paint", "blue", "--mode", "red", "green"],
        ["paint", "blue", "--mode=red", "green"],
        ["paint", "blue", "-vmred", "green"],
        ["paint", "blue", "--", "green"],
        ["paint", "--", "blue", "green"],
        ["paint", "blue", "green", "red", "rose"],
        ["framed", "remote", "blue", "green", "Blue"],
        ["resource", "blue", "two words.json"],
        ["directory", "blue", "nested directory/"],
        ["triple", "", "b", "bLue"],
    ],
)
def test_tuple_argument_parser(words):
    result = CliRunner().invoke(tuple_argument_fixture(), words)
    assert result.exit_code == 0, result.output


@pytest.mark.parametrize(
    "words",
    [
        ["paint", "blue"],
        ["paint", "blue", "--", "--mode"],
        ["framed", "remote", "blue", "green", "Blue", "blue"],
    ],
)
def test_tuple_argument_parser_errors(words):
    result = CliRunner().invoke(tuple_argument_fixture(), words)
    assert result.exit_code == 2, result.output
