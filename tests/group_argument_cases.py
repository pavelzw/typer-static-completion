"""Group argument and subcommand boundaries, before and after option parsing."""

from parsing_cases import ParsingCase

CASES = (
    ParsingCase("root-argument", "demo rem", "demo remote "),
    ParsingCase("command-after-argument", "demo root dep", "demo root deploy "),
    ParsingCase("argument-is-command", "demo remote rem", "demo remote remote "),
    ParsingCase("parent-option-value", "demo --profile bl", "demo --profile blue "),
    ParsingCase(
        "assigned-parent-option", "demo --profile=red rem", "demo --profile=red remote "
    ),
    ParsingCase("attached-parent-option", "demo -pred rem", "demo -pred remote "),
    ParsingCase("parent-options-stop", "demo root --pro", "demo root --pro"),
    ParsingCase("root-terminator", "demo -- rem", "demo -- remote "),
    ParsingCase(
        "terminator-to-child",
        "demo -- root deploy --mod",
        "demo -- root deploy --mode ",
    ),
    ParsingCase("child-argument", "demo root deploy bl", "demo root deploy blue "),
    ParsingCase(
        "child-option", "demo root deploy --mode ro", "demo root deploy --mode rose "
    ),
    ParsingCase(
        "parent-options-do-not-leak", "demo root deploy --pro", "demo root deploy --pro"
    ),
    ParsingCase("tuple-first", "demo root remote bl", "demo root remote blue "),
    ParsingCase(
        "tuple-second", "demo root remote blue gre", "demo root remote blue green "
    ),
    ParsingCase(
        "nested-parent-option",
        "demo root remote --mode ro",
        "demo root remote --mode rose ",
    ),
    ParsingCase(
        "tuple-options-stop",
        "demo root remote blue --mod",
        "demo root remote blue --mod",
    ),
    ParsingCase(
        "nested-command",
        "demo root remote blue green pa",
        "demo root remote blue green paint ",
    ),
    ParsingCase(
        "nested-child-scope",
        "demo root remote blue green paint --mode bL",
        "demo root remote blue green paint --mode Blue ",
    ),
    ParsingCase(
        "nested-terminator",
        "demo root remote -- blue green pa",
        "demo root remote -- blue green paint ",
    ),
    ParsingCase(
        "directory-argument",
        "demo root files nest",
        "demo root files nested\\ directory/",
    ),
    ParsingCase(
        "command-after-directory",
        "demo root files nested\\ directory sh",
        "demo root files nested\\ directory show ",
    ),
    ParsingCase(
        "optional-argument-is-command",
        "demo root optional show sh",
        "demo root optional show show ",
    ),
    ParsingCase(
        "optional-argument-not-skipped",
        "demo root optional sh",
        "demo root optional sh",
    ),
    ParsingCase(
        "empty-argument", 'demo root optional "" sh', 'demo root optional "" show '
    ),
    ParsingCase(
        "variadic-argument", "demo root many blue ro", "demo root many blue rose "
    ),
    ParsingCase(
        "variadic-consumes-commands", "demo root many blue sh", "demo root many blue sh"
    ),
    ParsingCase(
        "unknown-command", "demo root unknown remote bl", "demo root unknown remote bl"
    ),
)
