"""Shared parsing expectations, independent of any shell or generator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ParsingCase:
    name: str
    line: str
    completed: str

    @property
    def input(self) -> str:
        return self.line + "<TAB>"


CASES = (
    ParsingCase("scalar-positional", "demo paint bl", "demo paint blue "),
    ParsingCase(
        "variadic-positional", "demo paint red blue ro", "demo paint red blue rose "
    ),
    ParsingCase(
        "option-after-positional", "demo paint red --col", "demo paint red --color "
    ),
    ParsingCase(
        "option-before-positional",
        "demo paint --color blue ro",
        "demo paint --color blue rose ",
    ),
    ParsingCase(
        "variadic-interspersed",
        "demo paint red --tag blue rose bl",
        "demo paint red --tag blue rose blue ",
    ),
    ParsingCase(
        "repeat-option-value",
        "demo paint --tag red --tag bl",
        "demo paint --tag red --tag blue ",
    ),
    ParsingCase(
        "repeat-option-flag",
        "demo paint --tag red --tag",
        "demo paint --tag red --tag ",
    ),
    ParsingCase(
        "repeat-assigned-value",
        "demo paint --tag=red --tag=bl",
        "demo paint --tag=red --tag=blue ",
    ),
    ParsingCase("cluster-attached-value", "demo paint -qvcbl", "demo paint -qvcblue "),
    ParsingCase(
        "cluster-separated-value", "demo paint -qvc bl", "demo paint -qvc blue "
    ),
    ParsingCase(
        "cluster-consumed-value", "demo paint -qvcred bl", "demo paint -qvcred blue "
    ),
    ParsingCase("cluster-count-flags", "demo paint -vvvq bl", "demo paint -vvvq blue "),
    ParsingCase("cluster-parent-value", "demo -vkremote pa", "demo -vkremote paint "),
    ParsingCase("terminator-positional", "demo paint -- bl", "demo paint -- blue "),
    ParsingCase(
        "terminator-stops-options", "demo paint -- --col", "demo paint -- --col"
    ),
    ParsingCase(
        "terminator-as-value",
        "demo paint --token -- --col",
        "demo paint --token -- --color ",
    ),
    ParsingCase("root-target", "demo --target roo", "demo --target root "),
    ParsingCase(
        "group-target", "demo remote --target gre", "demo remote --target green "
    ),
    ParsingCase(
        "leaf-target",
        "demo remote paint --target bl",
        "demo remote paint --target blue ",
    ),
    ParsingCase(
        "parent-value-is-command",
        "demo --target remote pa",
        "demo --target remote paint ",
    ),
    ParsingCase(
        "parent-options-do-not-leak",
        "demo remote paint red --root-o",
        "demo remote paint red --root-o",
    ),
    ParsingCase(
        "scope-after-root-terminator",
        "demo -- remote --target gre",
        "demo -- remote --target green ",
    ),
    ParsingCase(
        "scope-after-group-terminator",
        "demo remote -- paint --target bl",
        "demo remote -- paint --target blue ",
    ),
    ParsingCase(
        "unknown-command-stays-invalid",
        "demo unknown remote pa",
        "demo unknown remote pa",
    ),
    ParsingCase(
        "unknown-nested-command",
        "demo remote unknown paint bl",
        "demo remote unknown paint bl",
    ),
    ParsingCase(
        "opaque-value-is-command",
        "demo --token remote pa",
        "demo --token remote paint ",
    ),
    ParsingCase(
        "opaque-value-is-option",
        "demo paint --token --tag bl",
        "demo paint --token --tag blue ",
    ),
)
