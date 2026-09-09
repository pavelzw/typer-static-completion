# typer-static-completions

[![CI](https://img.shields.io/github/actions/workflow/status/pavelzw/typer-static-completions/ci.yml?style=flat-square&branch=main)](https://github.com/pavelzw/typer-static-completions/actions/workflows/ci.yml)
[![conda-forge](https://img.shields.io/conda/vn/conda-forge/typer-static-completions?logoColor=white&logo=conda-forge&style=flat-square)](https://prefix.dev/channels/conda-forge/packages/typer-static-completions)
[![pypi-version](https://img.shields.io/pypi/v/typer-static-completions.svg?logo=pypi&logoColor=white&style=flat-square)](https://pypi.org/project/typer-static-completions)
[![python-version](https://img.shields.io/pypi/pyversions/typer-static-completions?logoColor=white&logo=python&style=flat-square)](https://pypi.org/project/typer-static-completions)

Generate static shell completions for typer applications

Status: initial Bash implementation. Typer introspection and Bash generation work
for nested commands, flags, choices, scalar/variadic arguments, and paths. Zsh,
Fish, PowerShell, file management, and CLI commands are still scaffolds. See
[TODO.md](TODO.md) for the remaining work.

```python
from typer_static_completions import generate
from myapp.cli import app

script = generate(app, "myapp", "bash")
```

Write the returned script to a file and source it in Bash. Completion stays
static: dynamic callback values are omitted by default. Explicit file fallback
is supported; hybrid delegation currently raises an error. Chain groups, group
arguments, tuple arity, and case-insensitive choices are not yet supported and
raise errors instead of generating approximate completions.

## Interactive screen snapshots

The first Bash path includes real PTY/Readline screen snapshots like those in
`commander-static-completion`, recording suggestions, inserted text, and cursor
position. The isolated snapshot environment provides Bash, pexpect, and pyte on
Linux/macOS. Ordinary unit tests can run without those integration dependencies.

```bash
pixi run -e snapshots test-snapshots
pixi run -e snapshots update-snapshots
```

Review changes under `tests/snapshots/` after updating. Missing or changed
snapshots fail checks; updating is forbidden in CI. The harness uses an isolated
80x24 terminal, named editing keys, timeouts, process cleanup, and sentinels that
fail if static completion invokes the CLI or Python. CI checks the snapshots on
Linux and macOS; Zsh/Fish screen coverage is the next priority.

Current snapshot baselines target the locked Bash 5.x environment. Unicode,
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
