"""Expected command-line tokens independently checked before snapshot updates."""

from dataclasses import dataclass, field

from typer_static_completion import GenerationOptions


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


CASES += [
    CoverageCase(
        "prefix-" + name,
        "demo show --value " + prefix,
        ("demo", "show", "--value", value),
    )
    for name, prefix, value in [
        ("dollar-single-quoted", "'dollar$(d", "dollar$(demo)"),
        ("dollar-escaped", r"dollar\$\(d", "dollar$(demo)"),
        ("dollar-double-quoted", '"dollar\\$(d', "dollar$(demo)"),
        ("backtick-single-quoted", "'tick`d", "tick`demo`"),
        ("backtick-escaped", r"tick\`d", "tick`demo`"),
        ("dollar-closed-quote", "'dollar$(d'", "dollar$(demo)"),
        ("dollar-concatenated-quote", "dollar'$(d", "dollar$(demo)"),
        ("colon-double-quoted", '"bracket[one]:t', "bracket[one]:two"),
        ("colon-closed-quote", "'bracket[one]:t'", "bracket[one]:two"),
        ("bracket-escaped", r"bracket\[o", "bracket[one]:two"),
        ("bracket-single-quoted", "'bracket[o", "bracket[one]:two"),
        ("colon-escaped", r"bracket\[one\]:t", "bracket[one]:two"),
        ("colon-single-quoted", "'bracket[one]:t", "bracket[one]:two"),
        ("backslash-escaped", r"slash\\p", r"slash\path"),
        ("backslash-single-quoted", r"'slash\p", r"slash\path"),
        ("double-quote-escaped", r"quote\"d", 'quote"double'),
        ("apostrophe-escaped", r"apos\'t", "apos'trophe"),
    ]
]
CASES += [
    CoverageCase(
        "prefix-assigned-" + name,
        "demo show --value=" + prefix,
        ("demo", "show", "--value=" + value),
    )
    for name, prefix, value in [
        ("dollar", "'dollar$(d", "dollar$(demo)"),
        ("colon", "'bracket[one]:t", "bracket[one]:two"),
        ("backslash", r"slash\\p", r"slash\path"),
    ]
]
