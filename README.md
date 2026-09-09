# typer-static-completions

[![CI](https://img.shields.io/github/actions/workflow/status/pavelzw/typer-static-completions/ci.yml?style=flat-square&branch=main)](https://github.com/pavelzw/typer-static-completions/actions/workflows/ci.yml)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/typer-static-completions?logoColor=white&logo=conda-forge&style=flat-square)](https://prefix.dev/channels/conda-forge/packages/typer-static-completions)
[![pypi-version](https://img.shields.io/pypi/v/typer-static-completions.svg?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/typer-static-completions)
[![python-version](https://img.shields.io/pypi/pyversions/typer-static-completions?logoColor=white&logo=python&style=flat-square)](https://pypi.org/project/typer-static-completions)

Generate static shell completions for typer applications

Status: initial Bash, Fish, and Zsh implementation. Typer introspection and generation work
for nested commands, flags, choices, scalar/variadic arguments, and paths.
The `write()` API supports build-time file generation. `CompletionSet`, PowerShell,
and CLI commands are still scaffolds. See
[TODO.md](TODO.md) for the remaining work.

```python
from typer_static_completions import generate
from myapp.cli import app

script = generate(app, "myapp", "bash")
```

Pass `"fish"` or `"zsh"` to target those shells. Write the returned script to a
file and source it in the corresponding shell (after `compinit` for Zsh). Completion stays
static: dynamic callback values are omitted by default. Explicit file fallback
is supported; hybrid delegation currently raises an error. Chain groups, group
arguments, tuple arity, and case-insensitive choices are not yet supported and
raise errors instead of generating approximate completions.

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

Current snapshot baselines target the locked Bash 5.x, Fish 4.x, and Zsh 5.9 environment. Unicode,
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
