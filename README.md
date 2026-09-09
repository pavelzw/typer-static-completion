# typer-static-completions

[![CI](https://img.shields.io/github/actions/workflow/status/pavelzw/typer-static-completions/ci.yml?style=flat-square&branch=main)](https://github.com/pavelzw/typer-static-completions/actions/workflows/ci.yml)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/typer-static-completions?logoColor=white&logo=conda-forge&style=flat-square)](https://prefix.dev/channels/conda-forge/packages/typer-static-completions)
[![pypi-version](https://img.shields.io/pypi/v/typer-static-completions.svg?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/typer-static-completions)
[![python-version](https://img.shields.io/pypi/pyversions/typer-static-completions?logoColor=white&logo=python&style=flat-square)](https://pypi.org/project/typer-static-completions)

Generate static shell completions for typer applications. Requires Python 3.11 or newer.

Status: initial Bash, Fish, and Zsh implementation. Typer introspection and generation work
for nested commands, flags, choices, scalar/variadic arguments, and paths.
The `write()` and `CompletionSet` APIs support build-time file generation and
staleness checks, including pyproject discovery. The CLI implements `generate`,
`sync`, and `check`; PowerShell, installation automation, and `verify` remain unimplemented. See
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

## Managing several CLIs and checking committed files

```python
from typer_static_completions import CompletionSet
from myapp.cli import app

completions = CompletionSet(
    {"myapp": app, "myadmin": "myapp.admin:app"},
    output_dir="completions",
)
print(completions.sync().report())
completions.check().raise_for_status()  # Use this line alone in CI.
```

Run `sync()` during generation and commit the resulting shell scripts **and**
`completions/.typer-static-completions.json`. Run only `check()` in CI so stale
files fail instead of being silently regenerated. Checks return missing, stale,
and orphaned paths, optional unified diffs, import failures (`skipped`), and
ownership conflicts. `check(diffs=False)` omits diffs, and `report(max_files=5)`
bounds the displayed details. The manifest itself appears in write/check results
when missing or changed. No check creates directories or modifies files.

The manifest records each file's owning CLI and content hash. By default, `sync()`
prunes recorded outputs that are no longer generated, including renamed commands
and removed shells. Handwritten files elsewhere in the directory remain intact.
An unmanaged destination with different content, or an orphan edited since its
last sync, blocks syncing before writes; inspect and move or remove the conflicting
file before retrying. Identical outputs from `write()` can be adopted. Use
`prune=False` to retain old outputs and their ownership for later cleanup.

String targets import a module and read a Typer instance, including nested
attributes such as `"myapp.cli:commands.app"`. Importing executes module code, but
wrapper functions and factories are never called to discover an app. Construct
factory-backed apps explicitly and pass their instances. A failed import appears
in `sync().skipped` while other apps are updated; its previous files and ownership
are retained. Any skipped app makes `check()` fail. `render()` and `trees()` raise
on failed imports to avoid silently returning incomplete results. Generation and
layout errors abort the operation before writing.

Use one `CompletionSet` per output directory. Writes are atomic per file; the
manifest is updated last so an interrupted sync can be retried. Concurrent syncs
are not supported.

### Discovering project entrypoints

```python
completions = CompletionSet.from_pyproject(
    "pyproject.toml",  # Omit to find the nearest one at or above cwd.
    output_dir="completions",
    overrides={"myapp": "myapp.cli:app"},  # If project.scripts points to main().
)
completions.sync()
```

Discovery reads `[project.scripts]` without importing modules. Overrides replace
**declared** script targets with import strings, Typer instances, or CommandTrees;
unknown names are errors. Factories must be called explicitly by your build code.
Targets need to be importable in the current environment: discovery does not
modify `sys.path` or change directories. Relative `output_dir` paths are relative
to cwd, even when the pyproject lives elsewhere.

Use `only=["myapp"]` to manage a subset. Outputs owned by other CLIs are preserved,
including previously removed entrypoints, and their targets are not imported.
Omit `only` for a full sync that can prune removed entrypoints; `only=[]` selects
no apps. Missing tables and malformed metadata fail rather than becoming empty
sets. An explicitly empty `[project.scripts]` table is allowed for projects that
have removed all their commands. TOML parsing uses the standard-library `tomllib`.

## Command line interface

Generate one shell's script from an importable Typer app:

```bash
pixi run typer-static-completions generate myapp.cli:app --prog-name myapp --shell fish -o myapp.fish
```

`generate` requires `--shell`; it has no default shell.
Omit `-o` (or use `-o -`) to emit only the script on stdout. Python import output
is redirected to stderr so it cannot corrupt the generated script.

For a project with `[project.scripts]`, generate or check all its completions:

```bash
pixi run typer-static-completions sync --app myapp=myapp.cli:app
pixi run typer-static-completions check --app myapp=myapp.cli:app --no-diff
```

`--app NAME=MODULE:APP` overrides a declared wrapper entrypoint. Repeat `--app`,
`--only NAME`, or `--shell bash --shell fish` to select several apps or shells.
`--pyproject PATH` selects metadata explicitly; otherwise the nearest pyproject
is used. `sync` and `check` select all three shells unless `--shell` narrows them.
The default output is `completions/` beside that file. An explicit
`--output-dir` is relative to cwd. `--no-prune` retains old outputs, and
`check --max-files 5` bounds diagnostics. Commit the scripts and ownership manifest,
then run `check` without `sync` in CI.

Exit codes are **0** for success, **1** for a failed check or a sync with skipped
apps, and **2** for usage, configuration, or operation errors. Sync reports go to
stdout; check reports and errors go to stderr. Import targets must already be
installed or importable in your environment.

To generate this CLI's own completions from the checkout:

```bash
pixi run typer-static-completions sync --app typer-static-completions=typer_static_completions.cli:app
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
