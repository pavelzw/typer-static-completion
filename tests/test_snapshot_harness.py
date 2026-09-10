"""The screen harness must fail clearly and clean up stalled shells."""

import os
import shlex
from pathlib import Path

import pytest

pytest.importorskip("pexpect")
pytest.importorskip("pyte")

from snapshot_harness import capture, keystrokes


@pytest.mark.parametrize(
    "value", ["demo<ENTER>", "demo\n", "demo<TAB:0>", "demo<TAB:1001>"]
)
def test_invalid_keys(value):
    with pytest.raises(ValueError):
        keystrokes(value)


def test_editing_keys():
    assert (
        keystrokes("a<LEFT:2><TAB><BACKSPACE><RIGHT><HOME><END>")
        == "a\x02\x02\t\x7f\x06\x01\x05"
    )


def test_timeout_reaps_worker(tmp_path: Path):
    pid_file = tmp_path / "pid"
    shell = tmp_path / "stalled shell"
    shell.write_text(
        f"#!/bin/sh\nprintf '%s' \"$$\" > {shlex.quote(str(pid_file))}\nprintf 'startup stall'\nexec /bin/sleep 30\n"
    )
    shell.chmod(0o755)
    with pytest.raises(AssertionError, match="startup stall"):
        capture("", "demo", executable=str(shell), timeout=2)
    with pytest.raises(ProcessLookupError):
        os.kill(int(pid_file.read_text()), 0)


@pytest.mark.parametrize("shell", ["bash", "fish", "zsh"])
def test_static_invocation_is_detected(shell):
    script = {
        "bash": "_bad() { demo; }; complete -F _bad demo\n",
        "fish": "function _bad; demo; end; complete -c demo -f -a '(_bad)'\n",
        "zsh": "_bad() { demo; }; compdef _bad demo\n",
    }[shell]
    with pytest.raises(AssertionError, match="invoked"):
        capture(script, "demo a<TAB>", shell=shell)


def test_output_is_bounded():
    from snapshot_harness import Transcript

    transcript = Transcript()
    with pytest.raises(AssertionError, match="exceeded"):
        transcript.write("x" * (1024 * 1024 + 1))


def test_startup_failure_retains_diagnostics(tmp_path):
    shell = tmp_path / "failed shell"
    shell.write_text("#!/bin/sh\nprintf 'startup failed'\nexit 1\n")
    shell.chmod(0o755)
    with pytest.raises(AssertionError, match="startup failed"):
        capture("", "demo", executable=str(shell))


def test_terminal_queries_can_be_split_across_reads():
    from snapshot_harness import TerminalProtocol

    replies: list[str] = []
    protocol = TerminalProtocol(replies.append)
    for part in (
        "\x1b[?",
        "u",
        "\x1b[>0q",
        "\x1b]11;?\x1b",
        "\\",
        "\x1bP+q6162\x1b\\",
        "\x1b[0c",
    ):
        protocol.write(part)
    assert replies == [
        "\x1b[?0u",
        "\x1bP>|XTerm(370)\x1b\\",
        "\x1b]11;rgb:0000/0000/0000\x1b\\",
        "\x1bP0+r6162\x1b\\",
        "\x1b[?1;2c",
    ]


def test_live_terminal_negotiation(tmp_path):
    shell = tmp_path / "querying shell"
    shell.write_text(
        "#!/bin/bash\n/bin/stty -echo -icanon min 1\n"
        "printf '\\033]777;TSC_READY\\007\\033[0c'\n"
        "seen=\nwhile IFS= read -r -n 1 char; do\n"
        "seen+=$char\n[[ $seen == *$'\\033[?1;2c' ]] && break\ndone\n"
        "printf '> negotiation complete\\033]777;TSC_DONE\\007'\nexec /bin/sleep 30\n"
    )
    shell.chmod(0o755)
    assert capture("", "probe", executable=str(shell)) == "> negotiation complete▏\n"


def test_zsh_autoload_matches_sourced_script(tmp_path):
    from fixtures import fixture

    from typer_static_completion import generate

    script = generate(fixture(), "demo", "zsh")
    (tmp_path / "_demo").write_text(script)
    loader = f"fpath=({shlex.quote(str(tmp_path))} $fpath)\nautoload -Uz _demo\ncompdef _demo demo\n"
    expected = capture(script, "demo dep<TAB>", shell="zsh")
    assert capture(loader, "demo dep<TAB>", shell="zsh") == expected


def test_fish_redraw_after_acknowledgement_is_retained(tmp_path):
    shell = tmp_path / "redrawing shell"
    shell.write_text(
        "#!/bin/sh\n/bin/stty -echo -icanon\n"
        "printf '\\033]777;TSC_READY\\007stale\\033]777;TSC_DONE\\007\\r\\033[K> redraw'\n"
        "exec /bin/sleep 30\n"
    )
    shell.chmod(0o755)
    assert capture("", "", shell="fish", executable=str(shell)) == "> redraw▏\n"


def test_zsh_waits_for_line_editor_before_sending_keys():
    from fixtures import fixture

    from typer_static_completion import generate

    # Delay between setup and ZLE activation. A READY emitted by setup allows
    # the terminal to echo the input while it is still in cooked mode.
    script = (
        "precmd() { local start=$SECONDS; while (( SECONDS == start )); do :; done; }\n"
    )
    script += generate(fixture(), "demo", "zsh")
    assert capture(script, "demo dep<TAB>", shell="zsh") == "> demo deploy ▏\n"
