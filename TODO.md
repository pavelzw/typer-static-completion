# Implementation and testing TODO

The CLI provides only `generate`. The Python API provides `generate()` and
`write()` for an explicit app or command tree. Bash, Fish, and Zsh are implemented;
PowerShell and dynamic delegation are not.

Use `../commander-static-completion` as the local reference, especially its
interactive screen harness and behavioral tests.

## Completed

- [x] Introspect Typer apps without executing command callbacks; preserve command
      scope, choices, boolean negations, paths, scalar/variadic arguments, and
      repeated/count options. Diagnose unsupported parser shapes.
- [x] Generate static Bash, Fish, and Zsh scripts without invoking Python or the
      CLI at completion time. Default dynamic values to omission.
- [x] Support `write()` with shell selection, custom layouts, dry runs, unchanged
      mtimes, validation before writing, and atomic replacement per file.
- [x] Load explicit module/app targets without calling wrappers or factories.
- [x] Implement CLI `generate` with required shell selection, stdout/file output,
      error handling, and stream/exit-code tests.
- [x] Record full generated scripts for demo, parsing, CLI, coverage, tuple, tuple-argument, group-argument, case-matching, Unicode, and word-break fixtures in all
      three shells, alongside 204 shared interactive screen cases and 12 Bash-only
      cases covering 72 word-break scenarios.
- [x] Test interactive completion for choices, quoted files, nested commands,
      assignments, short clusters, repeated flags, positional values, `--`, parent
      scope, two CLIs loaded together, and repeated sourcing.
- [x] Build an isolated PTY harness with a terminal emulator, named editing keys,
      cursor markers, bounded output/time, process cleanup, invocation sentinels,
      Fish terminal negotiation, and Zsh line-editor readiness synchronization.
- [x] Require explicit local snapshot updates and prevent updates in CI. Check
      interactive snapshots on Linux/macOS and portable tests on supported Python
      versions (3.11+) and operating systems.

## Snapshot coverage (priority)

- [x] Cover accented Unicode, colons, brackets, dollars, backticks, quotes, and
      backslashes. Verify completed argument values through the actual shell
      and reject substitution execution, alongside interactive screens.
- [x] Cover literal metacharacters already in escaped/quoted prefixes, including
      assignments, embedded quotes, and closed quotes. Check the actual argument
      values and reject substitution execution in every shell.
- [x] Cover CJK, single-code-point emoji, and decomposed/stacked accents at the
      end and middle of the line. Record exact editor state independently of
      display normalization, and place cursor markers by terminal cell.
- [x] Test custom Bash word-break settings for `:`, `=`, and `@`, including
      quoted/escaped prefixes and assignments; preserve Readline's special `@` prefix.
- [ ] Extend to multi-code-point emoji sequences, line wrapping, and
      control-character filenames.
- [x] Add cases for custom/disabled help flags, hidden commands/options,
      deprecated commands, and literal descriptions with descriptions disabled.
- [x] Support tuple options with per-position types, repeated occurrences, assigned
      and attached values, and interactive/full-file snapshots in all three shells.
- [x] Preserve case-sensitive/insensitive choice matching, with interactive and
      full-file snapshots covering options, arguments, tuples, and accented values.
- [x] Support tuple positional arguments, including interspersed options, `--`,
      and following scalar/variadic arguments, with interactive/full-file snapshots.
- [x] Support group arguments with native option boundaries and child-scope
      transitions; snapshot scalar, tuple, path, optional, and variadic arguments.
- [x] Detect `chain=True` in Typer constructor, callback, and `add_typer` settings
      before conversion drops it; test precedence and generation errors.
- [ ] Revisit chain groups when the supported Typer parser implements chaining.
      The locked 0.26.8 parser rejects a second command even with `chain=True`;
      keep the parser compatibility regression before adding completion snapshots.
- [ ] Support custom groups with interspersed options; their parser scans child
      tokens in the parent scope, so they require different dispatch rules.
- [ ] Add opt-in dynamic delegation and test it separately from static guarantees.
      Cover all DynamicPolicy variants in each shell.
- [ ] Expand native candidate verification while retaining interactive screens as the behavioral authority.

## API and compatibility

- [x] Make subcommand mappings read-only defensive copies, preserving declaration
      order. Keep trees unhashable and support edits via dataclasses.replace().
- [x] Remove unused shell detection, installation, candidate-verification, and
      PowerShell generator stubs. Reuse the public Shell enum in the CLI.
- [ ] Test the declared Typer range and retain useful compatibility checks for
      its vendored internals. Decide whether the optional upstream Click
      comparison should have a provided dependency or be replaced.
- [ ] Defer PowerShell until native candidate behavior, descriptions, syntax, and
      Windows integration tests are implemented.
- [ ] Benchmark script size and completion latency on large/deep Typer apps;
      turn compatibility failures into small regression fixtures.
