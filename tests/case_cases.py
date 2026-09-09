"""Case-sensitive and insensitive choice expectations."""

from parsing_cases import ParsingCase

CASES = (
    ParsingCase(
        "scope-resets", "demo --mode blue --strict bl", "demo --mode blue --strict bl"
    ),
    ParsingCase(
        "tuple-assigned-second", "demo --pair=blue rO", "demo --pair=blue Rose "
    ),
    ParsingCase("lowercase", "demo --mode bl", "demo --mode Blue "),
    ParsingCase("uppercase", "demo --mode BL", "demo --mode Blue "),
    ParsingCase("mixed", "demo --mode bL", "demo --mode Blue "),
    ParsingCase("canonical", "demo --mode Bl", "demo --mode Blue "),
    ParsingCase("assigned", "demo --mode=bL", "demo --mode=Blue "),
    ParsingCase("attached", "demo -mbL", "demo -mBlue "),
    ParsingCase(
        "repeated", "demo --mode red --mode bL", "demo --mode red --mode Blue "
    ),
    ParsingCase("positional", "demo bL", "demo Blue "),
    ParsingCase("terminator", "demo -- bL", "demo -- Blue "),
    ParsingCase("tuple-first", "demo --pair bL", "demo --pair Blue "),
    ParsingCase("tuple-second", "demo --pair Blue rO", "demo --pair Blue Rose "),
    ParsingCase("strict-match", "demo --strict Bl", "demo --strict Blue "),
    ParsingCase("strict-no-match", "demo --strict bl", "demo --strict bl"),
    ParsingCase("no-match", "demo --mode zz", "demo --mode zz"),
    ParsingCase("space", "demo --mode tW", "demo --mode Two\\ Words "),
    ParsingCase("accent", "demo --mode CAFÉ", "demo --mode Café "),
    ParsingCase("native-flag-matching", "demo --MO", "demo --MO"),
)
