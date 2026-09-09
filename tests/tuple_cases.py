"""Expected tuple completion behavior shared by snapshots and parser tests."""

from parsing_cases import ParsingCase

CASES = (
    ParsingCase(
        "path-second",
        "demo paint --resource blue two",
        "demo paint --resource blue two\\ words.json ",
    ),
    ParsingCase(
        "path-assigned",
        "demo paint --resource=blue two",
        "demo paint --resource=blue two\\ words.json ",
    ),
    ParsingCase("first", "demo paint --pair bl", "demo paint --pair blue "),
    ParsingCase(
        "second", "demo paint --pair blue gre", "demo paint --pair blue green "
    ),
    ParsingCase(
        "flags-resume",
        "demo paint --pair blue green --ver",
        "demo paint --pair blue green --verbose ",
    ),
    ParsingCase(
        "repeat-first",
        "demo paint --pair blue green --pair ro",
        "demo paint --pair blue green --pair rose ",
    ),
    ParsingCase(
        "repeat-second",
        "demo paint --pair blue green --pair red gro",
        "demo paint --pair blue green --pair red group ",
    ),
    ParsingCase("assigned-first", "demo paint --pair=bl", "demo paint --pair=blue "),
    ParsingCase(
        "assigned-second", "demo paint --pair=blue gre", "demo paint --pair=blue green "
    ),
    ParsingCase(
        "assigned-consumed",
        "demo paint --pair=blue green --ver",
        "demo paint --pair=blue green --verbose ",
    ),
    ParsingCase("attached-first", "demo paint -pbl", "demo paint -pblue "),
    ParsingCase("attached-second", "demo paint -pblue gre", "demo paint -pblue green "),
    ParsingCase(
        "cluster-second", "demo paint -vpblue gre", "demo paint -vpblue green "
    ),
    ParsingCase(
        "cluster-separated", "demo paint -vp blue gre", "demo paint -vp blue green "
    ),
    ParsingCase(
        "parent-command-values",
        "demo --pair paint paint pa",
        "demo --pair paint paint paint ",
    ),
    ParsingCase(
        "three-values", "demo paint --triple a b bl", "demo paint --triple a b blue "
    ),
    ParsingCase(
        "flag-looking-values",
        "demo paint --triple --verbose -- bl",
        "demo paint --triple --verbose -- blue ",
    ),
    ParsingCase(
        "empty-value", 'demo paint --triple "" b bl', 'demo paint --triple "" b blue '
    ),
    ParsingCase(
        "wrong-position", "demo paint --pair blue bl", "demo paint --pair blue bl"
    ),
)
