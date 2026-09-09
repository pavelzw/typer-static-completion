"""Expected fixed-arity positional completion across all shells."""

from parsing_cases import ParsingCase

CASES = (
    ParsingCase("first", "demo paint bl", "demo paint blue "),
    ParsingCase("second", "demo paint blue gre", "demo paint blue green "),
    ParsingCase(
        "following-variadic", "demo paint blue green ro", "demo paint blue green rose "
    ),
    ParsingCase(
        "variadic-continues",
        "demo paint blue green red ro",
        "demo paint blue green red rose ",
    ),
    ParsingCase(
        "flag-between-values",
        "demo paint blue --verbose gre",
        "demo paint blue --verbose green ",
    ),
    ParsingCase(
        "option-between-values",
        "demo paint blue --mode red gre",
        "demo paint blue --mode red green ",
    ),
    ParsingCase(
        "pending-option-value",
        "demo paint blue --mode ro",
        "demo paint blue --mode rose ",
    ),
    ParsingCase(
        "assigned-option",
        "demo paint blue --mode=red gre",
        "demo paint blue --mode=red green ",
    ),
    ParsingCase(
        "short-cluster", "demo paint blue -vmred gre", "demo paint blue -vmred green "
    ),
    ParsingCase("terminator-before", "demo paint -- bl", "demo paint -- blue "),
    ParsingCase(
        "terminator-between", "demo paint blue -- gre", "demo paint blue -- green "
    ),
    ParsingCase(
        "terminator-blocks-flags",
        "demo paint blue -- --mod",
        "demo paint blue -- --mod",
    ),
    ParsingCase(
        "option-after-tuple",
        "demo paint blue green --mod",
        "demo paint blue green --mode ",
    ),
    ParsingCase("leading-scalar", "demo framed rem", "demo framed remote "),
    ParsingCase(
        "tuple-after-scalar", "demo framed remote bl", "demo framed remote blue "
    ),
    ParsingCase(
        "tuple-second-after-scalar",
        "demo framed remote blue gre",
        "demo framed remote blue green ",
    ),
    ParsingCase(
        "following-scalar",
        "demo framed remote blue green Bl",
        "demo framed remote blue green Blue ",
    ),
    ParsingCase(
        "no-extra-positional",
        "demo framed remote blue green Blue bl",
        "demo framed remote blue green Blue bl",
    ),
    ParsingCase(
        "file", "demo resource blue two", "demo resource blue two\\ words.json "
    ),
    ParsingCase(
        "directory",
        "demo directory blue nest",
        "demo directory blue nested\\ directory/",
    ),
    ParsingCase("third-insensitive", "demo triple a b bL", "demo triple a b Blue "),
    ParsingCase("empty-value", 'demo triple "" b bL', 'demo triple "" b Blue '),
    ParsingCase("opaque-first", "demo triple bl", "demo triple bl"),
    ParsingCase("opaque-second", "demo triple a bl", "demo triple a bl"),
)
