# typer-static-completions

[![CI](https://img.shields.io/github/actions/workflow/status/pavelzw/typer-static-completions/ci.yml?style=flat-square&branch=main)](https://github.com/pavelzw/typer-static-completions/actions/workflows/ci.yml)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/typer-static-completions?logoColor=white&logo=conda-forge&style=flat-square)](https://prefix.dev/channels/conda-forge/packages/typer-static-completions)
[![pypi-version](https://img.shields.io/pypi/v/typer-static-completions.svg?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/typer-static-completions)
[![python-version](https://img.shields.io/pypi/pyversions/typer-static-completions?logoColor=white&logo=python&style=flat-square)](https://pypi.org/project/typer-static-completions)

Generate static shell completions for typer applications. Requires Python 3.11 or newer.

Status: initial Bash, Fish, and Zsh implementation. Typer introspection and generation work
for nested commands, flags, choices, tuple options, scalar/tuple/variadic arguments, and paths.
The CLI provides `generate`; the Python API provides `generate()` and `write()`.
PowerShell and dynamic delegation remain unimplemented. See
[TODO.md](TODO.md) for the remaining work.

```python
from typer_static_completions import generate
from myapp.cli import app

script = generate(app, "myapp", "bash")
```

Pass `"fish"` or `"zsh"` to target those shells. Write the returned script to a
file and source it in the corresponding shell (after `compinit` for Zsh). Completion stays
static: dynamic callback values are omitted by default. Explicit file fallback
is supported; hybrid delegation currently raises an error. The supported
Typer 0.26 parser accepts `chain=True` but does not execute chained commands.
Generation rejects this setting explicitly, including callback and `add_typer`
settings, before Typer discards it during command conversion. Chain completion
remains deferred until the supported parser can execute chains.

Tuple options such as `pair: tuple[Color, Path]` complete each value using its
own type. All three shells support `--pair blue path`, `--pair=blue path`,
attached short values, and repeated occurrences. `Param.values` holds the
per-position `ValueSpec` metadata for callers constructing command trees by hand.
Tuple positional arguments also complete each position using its own type;
options may appear between values, and subsequent scalar or variadic arguments
receive their own completions.

Groups can take scalar, tuple, or variadic arguments. Completion consumes their
values before offering subcommands, then switches to the child's scope. Like
Typer's default parser, group options must precede the first argument; a child
starts its own option parsing. Optional arguments still consume available words,
and variadic group arguments consume the remainder, including command names.
Custom groups with `allow_interspersed_args=True` are diagnosed as unsupported.

Choices configured with `case_sensitive=False` accept differently cased prefixes
and insert the declared spelling, including in tuple parameters. Case-sensitive
choices retain exact prefix matching. Matching uses lowercase prefixes, as in
Typer's completion, with non-ASCII casing governed by the shell locale.

The public `Shell` enum lists the three implemented shells. Generator subclasses
implement `render()` and `quote()`; custom generators can be registered under
additional string names. `verify.check_syntax()` checks scripts with a locally
installed shell's parser.

Command models are frozen, and each `Command` copies its subcommand mapping into
a read-only view. Changing the original dictionary does not change the tree.
Declaration order is preserved. Trees remain unhashable; use `dataclasses.replace()`
to construct modified versions. Subcommand views are not mutable dictionaries.

## Build-time generation and example

Run the example from this checkout:

```bash
pixi run example deploy --environment staging
pixi run example-completions
```

The second task calls [`write()`](typer_static_completions/core.py) from
[`examples/completions.py`](examples/completions.py), producing
`build/completions/bash/shipyard`, `build/completions/zsh/_shipyard`, and
`build/completions/fish/shipyard.fish`. The example is exercised by the CI test
suite. In your project, call the same API during your build or release process:

```python
from typer_static_completions import GenerationOptions, write
from myapp.cli import app

outputs = write(
    app,
    "myapp",
    output_dir="build/completions",
    options=GenerationOptions(regenerate_command="pixi run completions"),
)
```

Use `shells=["fish"]` to select shells, `dry_run=True` to preview the returned
path-to-content mapping without writes, or
`layout={"bash": "share/bash-completion/completions/{prog}"}` to override a
shell's destination beneath the output directory. Unchanged files keep their
modification times. Generation and destination checks finish before writing;
changed files are replaced individually, so an I/O failure can leave a partially
updated set. Custom paths cannot escape the output directory or collide.

To try completion in an interactive shell, run these commands from the checkout
in the corresponding shell. The `shipyard` function supplies the example command;
a packaged application would supply its own console entrypoint.

Bash:

```bash
shipyard() { pixi run example "$@"; }
source build/completions/bash/shipyard
```

Zsh:

```zsh
shipyard() { pixi run example "$@"; }
autoload -Uz compinit
compinit
source build/completions/zsh/_shipyard
```

Fish:

```fish
function shipyard
    pixi run example $argv
end
source build/completions/fish/shipyard.fish
```

Try typing `shipyard deploy --environment st` followed by TAB. Completion itself
runs entirely in the shell. For persistent installation, copy the Bash file to
`~/.local/share/bash-completion/completions/shipyard` when using bash-completion,
or source it from your Bash startup file. Copy the Fish file to
`~/.config/fish/completions/shipyard.fish` (or your `$XDG_CONFIG_HOME` equivalent).
For Zsh, copy `_shipyard` to a directory on `fpath` before calling `compinit`.
These installation steps are manual; generation does not edit shell profiles.

After changing the CLI, rerun `pixi run example-completions` and source or install
the updated files. For your own application, replace that task with your build's
generation command. The banner records the regeneration command for reference.

## Command line interface

Generate one shell's script from an importable Typer app:

```bash
pixi run typer-static-completions generate myapp.cli:app --prog-name myapp --shell fish -o myapp.fish
```

`generate` requires `--shell` and `--prog-name`. Omit `-o` (or use `-o -`) to emit
the script on stdout. Otherwise, it writes to exactly the specified path, creating
parent directories as needed. Relative paths are relative to the current working
directory. Import output goes to stderr so it cannot corrupt the generated script.

Targets must point to Typer instances, such as `myapp.cli:app`; wrapper functions
and factories are never called to discover an app. Targets must already be
importable in the current environment. For factory-backed applications, construct
the app explicitly and use the Python API.

Exit codes are **0** for success and **2** for usage or operation errors. There is
no project discovery, ownership manifest, or automatic installation. Regenerate
and install scripts through your project's build process when its CLI changes.

To generate this CLI's own Fish completion:

```bash
pixi run typer-static-completions generate typer_static_completions.cli:app --prog-name typer-static-completions --shell fish -o typer-static-completions.fish
```

The CLI is also available as `pixi run python -m typer_static_completions.cli`.

## Interactive screen snapshots

Bash, Fish, and Zsh have real interactive PTY screen snapshots like those in
`commander-static-completion`, recording suggestions, inserted text, and cursor
position. The isolated snapshot environment provides all three shells, pexpect, and pyte on
Linux/macOS. Ordinary unit tests can run without those integration dependencies.

```bash
pixi run -e snapshots test-snapshots
pixi run -e snapshots update-snapshots
```

Review changes under `tests/snapshots/` after updating. Each screen snapshot has
sections for all three shells. Full completion files sit alongside them in
`tests/snapshots/generated/demo.{bash,fish,zsh}`, making changes to the emitted
code and its size reviewable over time. Both kinds of snapshots use the same
update/check commands; full-script checks also run with ordinary unit tests. Missing or changed
snapshots fail checks; updating is forbidden in CI. The harness uses an isolated
80x24 terminal, named editing keys, timeouts, process cleanup, and sentinels that
fail if static completion invokes the CLI or Python. CI checks the snapshots on
Linux and macOS. Fish terminal capability negotiation is exercised by the harness.

The parsing matrix in `tests/parsing_cases.py` covers scalar/variadic arguments,
repeated options, count flags, short clusters, shadowed parent options, and `--`.
Its screen tests assert the expected completed line before comparing snapshots.
`tests/snapshots/parsing/` also checks two CLIs loaded together and sourced twice;
`tests/snapshots/generated/parsing.{bash,fish,zsh}` records the corresponding full
completion files. Separate tests verify the tricky cases against Typer's parser.

The CLI itself has four shared interactive cases in `tests/snapshots/cli/` and
full scripts in `tests/snapshots/generated/cli.{bash,fish,zsh}`.

The coverage fixture adds 25 shared screens for custom/disabled help flags,
hidden commands/options, deprecated commands, literal help descriptions, Unicode,
and escaped values. These cases use `C.UTF-8` and live in `tests/snapshots/coverage/`,
with full scripts in `tests/snapshots/generated/coverage.{bash,fish,zsh}`.
Completed lines are parsed by the actual shell using a controlled stub to verify
argument values and reject executable substitutions before snapshots can update.
Bash explicitly quotes literal candidates containing expansion syntax because
Readline's filename quoting alone can leave backticks executable. Custom help
aliases retain their configured order for deterministic output across processes.

The tuple cases in `tests/tuple_cases.py` have interactive screen snapshots and a
full generated-script fixture alongside the existing parsing matrix.

The tuple-argument fixture adds 24 shared screens covering interspersed options,
`--`, following scalar/variadic arguments, choices, paths, and directories.
Full scripts live in `tests/snapshots/generated/tuple-arguments.{bash,fish,zsh}`.

The group-argument fixture adds 27 shared screens for parent arguments, nested
groups, option boundaries, `--`, paths, and optional/variadic arguments.
Full scripts live in `tests/snapshots/generated/group-arguments.{bash,fish,zsh}`.

The case-matching fixture adds 21 shared interactive screens for insensitive
options, arguments, tuple positions, ambiguous matches, and accented values,
plus sensitive-choice regressions. Full scripts live in
`tests/snapshots/generated/case.{bash,fish,zsh}`.

Current snapshot baselines target the locked Bash 5.x, Fish 4.x, and Zsh 5.9 environment. Broader Unicode coverage (including wide and combining characters),
custom word-break settings, unusual shell parsing modes, and filenames containing
control characters still need broader coverage.

## Installation

This project is managed by [pixi](https://pixi.sh).
You can install the package in development mode using:

```bash
git clone https://github.com/pavelzw/typer-static-completions
cd typer-static-completions

pixi run pre-commit-install
pixi run test
```
