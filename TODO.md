# Implementation and testing TODO

The current changes define an API scaffold. All generation, introspection,
management, CLI, and verification operations still raise `NotImplementedError`.
The interface tests do not establish working shell completion.

Use `../commander-static-completion` as the local reference, especially
`test/snapshots.test.js`, `test/snapshot-harness.js`,
`test/snapshot-harness.test.js`, `test/behavior.test.js`, and
`test/bash-readline.test.js`. Its interactive snapshots already exist; its
representative generated-script snapshots are still a TODO.

## First milestone: working completion with interactive screen snapshots

Interactive screen snapshots like Commander's are a top priority. Build the PTY
harness alongside the first working generator and extend both to Bash, Zsh, and
Fish before starting file management or CLI convenience features.

- [ ] Deliver a minimal end-to-end path from a Typer fixture to a generated script
      to a real interactive shell screen snapshot. Capture visible suggestions,
      inserted text, and cursor position from the start.
- [ ] Require reviewed interactive snapshots for each shell's initial support:
      unique and ambiguous completion, nested commands, choices, quoted paths,
      and cursor-in-the-middle editing.
- [ ] Include explicit local snapshot updates and a required shell-integration
      CI check in this milestone. Expand the shared case matrix with each new
      completion feature.

Generated-script snapshots and candidate assertions supplement this milestone;
real interactive screen coverage is part of the acceptance criteria. The detailed
harness and scenario checklist is in section 3.

## 1. Resolve contracts before implementation

- [ ] Decide the static guarantee. Commander never invokes the CLI at completion
      time; this scaffold defaults to `DynamicPolicy.DELEGATE`. Prefer a static
      default with explicit hybrid opt-in if matching Commander is the goal.
      Document and test all four policies, including no filesystem fallback for
      `OMIT` (Bash's unconditional `-o default` would violate that).
- [ ] Choose deep immutability or explicitly mutable mappings for `Command` and
      `CommandTree`. Frozen dataclasses alone neither freeze `subcommands` nor
      make these trees hashable. Test the chosen contract precisely.
- [ ] Preserve enough parser metadata: empty groups versus leaf commands,
      group argument boundaries, directory-only paths (`file_okay=False`),
      case-insensitive choices, tuple arity, repeatable/count flags, chain groups,
      and option parsing settings. Diagnose unsupported behavior explicitly.
- [ ] Resolve hidden filtering: `include_hidden=True` must not be undone by
      `Command.options` / `arguments` always returning only visible parameters.
- [ ] Define entrypoint loading. Many `[project.scripts]` targets are wrapper
      functions, not Typer instances (including this package's proposed `main`).
      Support explicit app mappings/factories without executing arbitrary CLI
      entrypoints to discover an app. Align `load_app`'s return type and docs.
- [ ] Make third-party shell registration consistent: `Generator.shell` and
      `available_shells()` currently use the closed `Shell` enum, despite the
      advertised support for arbitrary registered names.
- [ ] Define failure semantics for `CompletionSet`: failed imports must make
      checks fail visibly and must never turn existing files into prune targets.
      Track file ownership; retain handwritten files, and validate custom layouts
      for collisions and paths escaping the managed output directory.

## 2. First working implementation

- [ ] Implement model traversal, lookup, and parameter helpers with behavioral
      tests; replace the placeholder assertion in `tests/test_core.py`.
- [ ] Implement the Typer adapter with synthetic apps: single-command collapse,
      nested groups, aliases, boolean negations, enum choices, paths/files,
      custom help flags, hidden/deprecated entries, and callback detection.
      Test actual extracted trees, not only the existence of private attributes.
- [ ] Add fixtures for groups/options whose values look like command names.
      Walk tokens using parameter arity and scope rather than matching every
      non-flag word against a list of paths.
- [ ] Implement registry and `generate()` for Bash, Zsh, and Fish. Start with
      commands, flags, choices, positional values, and native file completion.
      Ensure stable output, final newlines, and collision-resistant helper names.
- [ ] Test literal escaping separately for shell strings and Zsh completion specs:
      apostrophes, quotes, colons, brackets, dollars, backticks, backslashes,
      whitespace, Unicode, and shell substitution syntax. Syntax checks alone
      cannot detect dropped characters or unintended evaluation.
- [ ] Exercise two generated CLIs loaded together, repeated sourcing, and Zsh
      autoload installation through `fpath` / `#compdef`.

## 3. Snapshot tests (priority)

### Shared fixtures and fast checks

- [ ] Create `tests/fixtures.py` and a shared case matrix consumed by every shell.
      Include both hand-built trees and real Typer apps to cover the adapter.
- [ ] Implement syntax checks and native candidate tests. Bash `COMPREPLY` and
      Fish `complete -C` are useful fast checks; mocked Zsh `_arguments` only
      tests dispatch and cannot prove actual insertion or candidate behavior.
- [ ] Add deterministic generated-script snapshots for representative fixtures
      in each shell. Keep versions/timestamps out by default; assert identical
      output across repeated generation. Review these alongside behavioral tests.

### Interactive screen snapshots like Commander (first-milestone requirement)

- [ ] Build `tests/snapshot_harness.py`: launch actual interactive Bash, Zsh,
      and Fish in a PTY, source generated scripts, and drive their line editors.
      Use a terminal emulator to interpret redraws and capture the final screen
      with an explicit cursor marker (`▏`); stripping ANSI escapes is insufficient.
      Evaluate a Python PTY/emulator stack against Commander's harness behavior.
- [ ] Use readable inputs such as `demo deploy --color r<TAB>` and
      `demo deploy --color r --verbose<LEFT:10><TAB>`. Support named editing keys,
      reject raw control characters/Enter, and bound repetition counts.
- [ ] Store one reviewed `tests/snapshots/<case>.snap` per scenario, containing
      the input and separate Bash/Fish/Zsh screen sections. Preserve insertion,
      cursor position, suggestion descriptions, quoting, and trailing spaces
      where they affect editing behavior.
- [ ] Start with unique/ambiguous/no matches, root/nested commands, choices,
      `--option=value`, boolean negations, filenames containing spaces or quotes,
      directories, unfinished quotes, escaped spaces, and cursor-in-the-middle.
      Extend to `--`, attached short values/clusters, repeatable/variadic/tuple
      values, parent option scope, help flags, and chain groups as implemented.
      Translate Commander cases to Typer semantics rather than copying defaults
      and help-command behavior that Typer does not share.
- [ ] Isolate shell configuration, history, working-directory fixtures, prompt,
      locale, terminal size (80x24), and autosuggestions. Use controlled child
      environments, with shell executable overrides and recorded shell versions.
- [ ] Synchronize on readiness and completion acknowledgements; answer terminal
      capability queries (especially Fish). Bound time and output; clean up the
      PTY and all child processes on success, startup failure, and timeout.
- [ ] Test the harness itself: malformed keys, startup failure, terminal query
      replies, timeouts with useful transcripts, and no surviving child process.
- [ ] For static cases, make the CLI executable a sentinel that records invocation
      and remove runtime executables from the child PATH after setup. Assert TAB
      never launches the CLI/Python. Test opt-in dynamic delegation separately.
- [ ] Add proposed Pixi tasks `test-snapshots` and `update-snapshots`. Missing or
      changed snapshots must fail normal tests; updates must be explicit, local,
      and rejected in CI. Print a focused diff and regeneration instructions.
- [ ] Add a dedicated Linux/macOS shell-integration CI job with locked shell and
      harness dependencies. Required shells must fail if missing in that job;
      keep portable Python unit tests on the existing OS/Python matrix. Document
      local optional skips and any deliberate platform-specific snapshots.
      Run `pixi lock` after changing `pixi.toml`.

## 4. Management, CLI, and packaging

- [ ] Implement `write()` and `CompletionSet` after the generation path works:
      dry runs, deterministic diffs, missing/stale/orphan reports, bounded report
      output, unchanged mtimes, safe writes, and the failure/pruning rules above.
- [ ] Implement CLI generate/sync/check/verify with stdout/stderr and exit-code
      tests. Treat installation as a later feature with explicit destinations;
      avoid automatic shell-profile changes.
- [ ] Add a runnable example and generate its completions in CI. Document build-
      time generation, installation per shell, regeneration, and static limits.
- [ ] Validate built wheels/sdists in clean environments, including subpackages,
      runtime dependencies, the console entrypoint, and typed API distribution.
      Verify Pixi-built package metadata also declares runtime requirements.
- [ ] Test the declared Typer range and Python 3.10 fallback for TOML parsing.
      Keep compatibility tests for private Typer access; the current upstream
      Click comparison skips when Click is absent, so decide whether to provide
      Click as a test dependency or replace that check with a useful invariant.
- [ ] Defer PowerShell until the three-shell path is tested; then implement native
      `CompletionResult` behavior, descriptions, syntax validation, and Windows
      integration tests before claiming Windows PowerShell 5.1/pwsh support.
- [ ] Benchmark script size and completion latency on large/deep real Typer apps,
      and turn compatibility failures into small regression fixtures.

Suggested order: resolve the contracts needed for the first fixture, build the
interactive harness alongside one working shell path, add reviewed screen
snapshots and CI, then extend generators and interactive snapshots to the other
two shells. File management and CLI convenience follow that milestone. Keep the current scaffold explicitly unreleased
as functionality until that first path works.
