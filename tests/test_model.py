"""Immutable command trees preserve stable output and declaration order."""

from dataclasses import replace

import pytest

from typer_static_completion import Command, CommandTree, generate


def test_source_mapping_mutations_do_not_change_generation():
    children = {
        "first": Command(("group", "first")),
        "second": Command(("group", "second")),
    }
    group = Command(("group",), subcommands=children)
    roots = {"group": group}
    tree = CommandTree("demo", Command((), subcommands=roots))
    before = generate(tree)
    children.clear()
    roots.clear()
    assert tree.paths() == ("group", "group first", "group second")
    assert generate(tree) == before


def test_nested_mappings_are_read_only():
    child = Command(("child",))
    tree = CommandTree("demo", Command((), subcommands={"child": child}))
    for node in tree.walk():
        with pytest.raises(TypeError):
            node.subcommands["new"] = Command(("new",))  # type: ignore[index]
    with pytest.raises(TypeError):
        hash(tree)


def test_replace_creates_an_independent_tree():
    tree = CommandTree("demo", Command((), subcommands={"first": Command(("first",))}))
    updated = replace(
        tree,
        root=replace(
            tree.root,
            subcommands={**tree.root.subcommands, "second": Command(("second",))},
        ),
    )
    assert tree.paths() == ("first",)
    assert updated.paths() == ("first", "second")
    assert tree == replace(tree, root=replace(tree.root))
