import shlex

import pytest
from fixtures import tuple_fixture
from tuple_cases import CASES
from typer.testing import CliRunner

from typer_static_completion import (
    Command,
    CommandTree,
    DynamicPolicy,
    GenerationOptions,
    IntrospectionError,
    Param,
    ParamKind,
    ValueKind,
    ValueSpec,
    from_app,
    generate,
)


def test_tuple_metadata():
    command = from_app(tuple_fixture(), "demo").find(["paint"])
    assert command is not None
    pair = next(p for p in command.options if p.name == "pair")
    assert pair.nargs == 2
    assert [v.value_kind for v in pair.values] == [ValueKind.CHOICE, ValueKind.CHOICE]
    assert "blue" in pair.values[0].choices
    assert pair.values[1].choices == ("group", "green")
    resource = next(p for p in command.options if p.name == "resource")
    assert resource.values[1].value_kind is ValueKind.FILE


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.name)
def test_tuple_parser(case):
    words = shlex.split(case.completed)[1:]
    if case.name in ("first", "repeat-first", "assigned-first", "attached-first"):
        words.append("green")
    result = CliRunner().invoke(tuple_fixture(), words)
    expected_exit = 2 if case.name == "wrong-position" else 0
    assert result.exit_code == expected_exit, result.output


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_tuple_dynamic_policy_and_missing_metadata(shell):
    param = Param(
        ParamKind.OPTION,
        "pair",
        ValueKind.OPAQUE,
        flags=("--pair",),
        nargs=2,
        values=(ValueSpec(ValueKind.OPAQUE), ValueSpec(ValueKind.DYNAMIC)),
    )
    tree = CommandTree("demo", Command((), params=(param,)))
    assert tree.has_dynamic_params
    for policy in (DynamicPolicy.ERROR, DynamicPolicy.DELEGATE):
        with pytest.raises(IntrospectionError, match="Dynamic callbacks"):
            generate(tree, shell=shell, options=GenerationOptions(dynamic=policy))
    for policy in (DynamicPolicy.OMIT, DynamicPolicy.FILE):
        generate(tree, shell=shell, options=GenerationOptions(dynamic=policy))
    from dataclasses import replace

    invalid = CommandTree("demo", Command((), params=(replace(param, values=()),)))
    with pytest.raises(IntrospectionError, match="metadata for every value"):
        generate(invalid, shell=shell)
