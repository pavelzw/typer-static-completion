"""Reviewed interactive screens: local updates are explicit and forbidden in CI."""

import os
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from case_cases import CASES as CASE_CHOICE_CASES
from coverage_cases import CASES as COVERAGE_CASES
from fixtures import fixture, parsing_fixture
from parsing_cases import CASES as PARSING_CASES
from snapshot_assertions import assert_snapshot
from snapshot_harness import capture
from tuple_argument_cases import CASES as TUPLE_ARGUMENT_CASES
from tuple_cases import CASES as TUPLE_CASES

from typer_static_completions import (
    Command,
    CommandTree,
    Param,
    ParamKind,
    ValueKind,
    generate,
)

CASES = {
    "subcommand": "demo dep<TAB>",
    "ambiguous-subcommands": "demo ta<TAB><TAB>",
    "no-match": "demo zzz<TAB>",
    "nested-command": "demo remote a<TAB>",
    "choice": "demo deploy --color bl<TAB>",
    "ambiguous-choice": "demo deploy --color r<TAB><TAB>",
    "assignment": "demo deploy --color=bl<TAB>",
    "short-attached": "demo deploy -cbl<TAB>",
    "negation": "demo deploy --no-c<TAB>",
    "space-choice": "demo deploy --color two<TAB>",
    "empty-option-value": 'demo --profile "" dep<TAB>',
    "apostrophe-choice": "demo deploy --color quote<TAB>",
    "apostrophe-file": "demo deploy --config quote<TAB>",
    "attached-file": "demo deploy --config=two<TAB>",
    "file": "demo deploy --config two<TAB>",
    "quoted-file": 'demo deploy --config "two<TAB>',
    "quoted-choice": 'demo deploy --color "two<TAB>',
    "escaped-choice": "demo deploy --color two\\ w<TAB>",
    "directory": "demo deploy --directory nest<TAB>",
    "cursor-middle": "demo deploy --color bl --no-cache<LEFT:11><TAB>",
    "option-value-is-command": "demo --profile remote dep<TAB>",
}


@pytest.mark.parametrize("name,input", CASES.items())
def test_screen(name, input):
    if os.environ.get("UPDATE_SNAPSHOTS") == "1" and os.environ.get("CI"):
        pytest.fail("Snapshot updates are disabled in CI")
    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(generate(fixture(), "demo", shell), input, shell=shell)
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(Path(__file__).with_name("snapshots") / f"{name}.snap", actual)


@pytest.mark.parametrize("case", PARSING_CASES, ids=lambda case: case.name)
def test_parsing_screen(case):
    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(
            generate(parsing_fixture(), "demo", shell), case.input, shell=shell
        )
        assert screen == f"> {case.completed}▏\n", f"{shell}: {case.name}\n{screen}"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {case.input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "parsing" / f"{case.name}.snap", actual
    )


@pytest.mark.parametrize(
    "program,line,completed",
    [
        ("demo", "demo paint bl", "demo paint blue "),
        ("other", "other az", "other azure "),
    ],
)
def test_multiple_scripts_and_repeated_sourcing(program, line, completed):
    other = CommandTree(
        "other",
        Command(
            (),
            params=(
                Param(
                    ParamKind.ARGUMENT,
                    "color",
                    ValueKind.CHOICE,
                    choices=("amber", "azure"),
                ),
            ),
        ),
    )
    sections = []
    for shell in ("bash", "fish", "zsh"):
        scripts = generate(parsing_fixture(), "demo", shell) + generate(
            other, shell=shell
        )
        sentinel = (
            "function other; printf invoked > invoked; end\n"
            if shell == "fish"
            else "other() { printf invoked > invoked; }\n"
        )
        screen = capture(scripts + scripts + sentinel, line + "<TAB>", shell=shell)
        assert screen == f"> {completed}▏\n", f"{shell}: {screen}"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = (
        f"Input: {line}<TAB>\n\nSetup: demo and other loaded twice\n\n"
        + "\n---\n\n".join(sections)
    )
    assert_snapshot(
        Path(__file__).with_name("snapshots")
        / "parsing"
        / f"multiple-scripts-{program}.snap",
        actual,
    )


@pytest.mark.parametrize(
    "name,line,completed",
    [
        (
            "command",
            "typer-static-completions gen",
            "typer-static-completions generate ",
        ),
        (
            "shell",
            "typer-static-completions generate --shell f",
            "typer-static-completions generate --shell fish ",
        ),
        (
            "output-option",
            "typer-static-completions generate --out",
            "typer-static-completions generate --output ",
        ),
        (
            "program-name-option",
            "typer-static-completions generate --prog-n",
            "typer-static-completions generate --prog-name ",
        ),
    ],
)
def test_cli_screen(name, line, completed):
    from typer_static_completions.cli import build_cli

    sections = []
    for shell in ("bash", "fish", "zsh"):
        sentinel = (
            "function typer-static-completions; printf invoked > invoked; end\n"
            if shell == "fish"
            else "typer-static-completions() { printf invoked > invoked; }\n"
        )
        screen = capture(
            generate(build_cli(), "typer-static-completions", shell) + sentinel,
            line + "<TAB>",
            shell=shell,
        )
        assert screen == f"> {completed}▏\n"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {line}<TAB>\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "cli" / f"{name}.snap", actual
    )


@pytest.mark.parametrize("case", COVERAGE_CASES, ids=lambda case: case.name)
def test_extended_coverage_screen(case, tmp_path):
    import shutil
    import subprocess

    from fixtures import coverage_fixture

    sections = []
    for shell in ("bash", "fish", "zsh"):
        sentinel = (
            "function demo; printf invoked > invoked; end\n"
            if shell == "fish"
            else "demo() { printf invoked > invoked; }\n"
        )
        script = sentinel + generate(
            coverage_fixture(), "demo", shell, options=case.options
        )
        screen = capture(script, case.line + "<TAB>", shell=shell, locale="C.UTF-8")
        assert screen.startswith("> ") and screen.count("▏") == 1
        # Parse the completed line in its actual shell. A controlled demo stub
        # reports substitutions separately; no real application is executed.
        completed = screen[2:].replace("▏", "").strip()
        stub = (
            "function demo; if test (count $argv) -eq 0; printf expansion >&2; end; printf '%s\\0' $argv; end\n"
            if shell == "fish"
            else 'demo() { if [ "$#" -eq 0 ]; then printf expansion >&2; fi; printf \'%s\\0\' "$@"; }\n'
        )
        executable = shutil.which(shell)
        assert executable is not None
        flags = {
            "bash": ["--noprofile", "--norc"],
            "fish": ["--no-config"],
            "zsh": ["-f"],
        }[shell]
        result = subprocess.run(
            [executable, *flags, "-c", stub + completed],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=tmp_path,
            env={"PATH": "/nonexistent", "LC_ALL": "C.UTF-8", "HOME": str(tmp_path)},
        )
        assert result.returncode == 0 and not result.stderr, (
            shell,
            screen,
            result.stderr,
        )
        assert result.stdout.rstrip("\0").split("\0") == list(case.expected[1:]), (
            shell,
            screen,
        )
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {case.line}<TAB>\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "coverage" / f"{case.name}.snap", actual
    )


@pytest.mark.parametrize(
    "include_help", [True, False], ids=["descriptions", "no-descriptions"]
)
def test_coverage_descriptions(include_help):
    from fixtures import coverage_fixture

    from typer_static_completions import GenerationOptions

    sections = []
    for shell in ("bash", "fish", "zsh"):
        sentinel = (
            "function demo; printf invoked > invoked; end\n"
            if shell == "fish"
            else "demo() { printf invoked > invoked; }\n"
        )
        script = sentinel + generate(
            coverage_fixture(),
            "demo",
            shell,
            options=GenerationOptions(include_help=include_help),
        )
        screen = capture(
            script, "demo show --<TAB><TAB>", shell=shell, locale="C.UTF-8"
        )
        if shell in ("fish", "zsh"):
            assert ('Use [x]: "$HOME", `demo`, and $(demo).' in screen) == include_help
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = "Input: demo show --<TAB><TAB>\n\n" + "\n---\n\n".join(sections)
    name = "descriptions" if include_help else "no-descriptions"
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "coverage" / f"{name}.snap", actual
    )


@pytest.mark.parametrize("case", TUPLE_CASES, ids=lambda case: case.name)
def test_tuple_screen(case):
    from fixtures import tuple_fixture

    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(
            generate(tuple_fixture(), "demo", shell), case.input, shell=shell
        )
        assert screen == f"> {case.completed}▏\n", f"{shell}: {case.name}\n{screen}"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {case.input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "tuple" / f"{case.name}.snap", actual
    )


@pytest.mark.parametrize("case", CASE_CHOICE_CASES, ids=lambda case: case.name)
def test_case_choice_screen(case):
    from fixtures import case_fixture

    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(
            generate(case_fixture(), "demo", shell),
            case.input,
            shell=shell,
            locale="C.UTF-8",
        )
        completed = case.completed
        if shell == "fish":
            # Native Fish quotes a replacement containing spaces and also
            # matches flag names without regard to case.
            completed = {
                "space": "demo --mode 'Two Words' ",
                "native-flag-matching": "demo --mode ",
            }.get(case.name, completed)
        assert screen == f"> {completed}▏\n", f"{shell}: {case.name}\n{screen}"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {case.input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "case" / f"{case.name}.snap", actual
    )


@pytest.mark.parametrize("prefix", ["r", ""], ids=["ambiguous", "empty"])
def test_case_choice_ambiguous_screen(prefix):
    from fixtures import case_fixture

    sections = []
    input = f"demo --mode {prefix}<TAB:3>"
    for shell in ("bash", "fish", "zsh"):
        screen = capture(
            generate(case_fixture(), "demo", shell),
            input,
            shell=shell,
            locale="C.UTF-8",
        )
        assert "RED" in screen and "Rose" in screen, (shell, screen)
        assert ("Blue" in screen) == (prefix == "")
        assert ("Café" in screen) == (prefix == "")
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots")
        / "case"
        / ("ambiguous.snap" if prefix else "empty.snap"),
        actual,
    )


@pytest.mark.parametrize("case", TUPLE_ARGUMENT_CASES, ids=lambda case: case.name)
def test_tuple_argument_screen(case):
    from fixtures import tuple_argument_fixture

    sections = []
    for shell in ("bash", "fish", "zsh"):
        screen = capture(
            generate(tuple_argument_fixture(), "demo", shell), case.input, shell=shell
        )
        assert screen == f"> {case.completed}▏\n", f"{shell}: {case.name}\n{screen}"
        sections.append(f"Shell: {shell}\n\n{screen}")
    actual = f"Input: {case.input}\n\n" + "\n---\n\n".join(sections)
    assert_snapshot(
        Path(__file__).with_name("snapshots") / "tuple-arguments" / f"{case.name}.snap",
        actual,
    )
