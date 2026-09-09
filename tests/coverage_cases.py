"""Expected command-line tokens independently checked before snapshot updates."""

from dataclasses import dataclass, field

from typer_static_completions import GenerationOptions


@dataclass(frozen=True)
class CoverageCase:
    name: str
    line: str
    expected: tuple[str, ...]
    options: GenerationOptions = field(default_factory=GenerationOptions)


CASES = [
    CoverageCase(
        "single-quoted-apostrophe",
        "demo show --value 'apos",
        ("demo", "show", "--value", "apos'trophe"),
    ),
    CoverageCase(
        "apostrophe",
        "demo show --value apos",
        ("demo", "show", "--value", "apos'trophe"),
    ),
    CoverageCase(
        "quoted-backtick",
        'demo show --value "tick',
        ("demo", "show", "--value", "tick`demo`"),
    ),
    CoverageCase(
        "quoted-dollar",
        'demo show --value "doll',
        ("demo", "show", "--value", "dollar$(demo)"),
    ),
    CoverageCase(
        "single-quoted-backtick",
        "demo show --value 'tick",
        ("demo", "show", "--value", "tick`demo`"),
    ),
    CoverageCase(
        "unicode-prefix", "demo show --value café", ("demo", "show", "--value", "café")
    ),
    CoverageCase(
        "unicode-before-cursor",
        "demo show --value café --ass --secret<LEFT:9>",
        ("demo", "show", "--value", "café", "--assist", "--secret"),
    ),
    CoverageCase("root-help", "demo --ass", ("demo", "--assist")),
    CoverageCase("child-help", "demo show --ass", ("demo", "show", "--assist")),
    CoverageCase(
        "help-omitted",
        "demo show --ass",
        ("demo", "show", "--ass"),
        GenerationOptions(include_help_option=False),
    ),
    CoverageCase("help-disabled", "demo bare --h", ("demo", "bare", "--h")),
    CoverageCase("hidden-command-omitted", "demo internal-s", ("demo", "internal-s")),
    CoverageCase(
        "hidden-command-included",
        "demo internal-s",
        ("demo", "internal-secret"),
        GenerationOptions(include_hidden=True),
    ),
    CoverageCase("hidden-option-omitted", "demo show --sec", ("demo", "show", "--sec")),
    CoverageCase(
        "hidden-option-included",
        "demo show --sec",
        ("demo", "show", "--secret"),
        GenerationOptions(include_hidden=True),
    ),
    CoverageCase(
        "deprecated-included", "demo legacy-dep", ("demo", "legacy-deprecated")
    ),
    CoverageCase(
        "deprecated-omitted",
        "demo legacy-dep",
        ("demo", "legacy-dep"),
        GenerationOptions(include_deprecated=False),
    ),
    *[
        CoverageCase(
            name, "demo show --value " + prefix, ("demo", "show", "--value", value)
        )
        for name, prefix, value in [
            ("unicode", "ca", "café"),
            ("brackets", "brack", "bracket[one]:two"),
            ("dollar-substitution", "doll", "dollar$(demo)"),
            ("backtick-substitution", "tick", "tick`demo`"),
            ("double-quote", "quot", 'quote"double'),
            ("backslash", "slas", "slash\\path"),
        ]
    ],
]
