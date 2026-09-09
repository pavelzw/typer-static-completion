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
- [x] Record full generated scripts for demo, parsing, and CLI fixtures in all
      three shells, alongside 54 shared interactive screen cases.
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

- [ ] Extend escaping tests to Unicode, colons, brackets, dollars, backticks,
      backslashes, unusual word-break settings, and control-character filenames.
      Verify actual insertion and absence of evaluation, not just shell syntax.
- [ ] Add cases for custom help configuration and hidden/deprecated parameters.
- [ ] Implement and snapshot tuple values, chain groups, group arguments, and
      case-insensitive choices before claiming support.
- [ ] Add opt-in dynamic delegation and test it separately from static guarantees.
      Cover all DynamicPolicy variants in each shell.
- [ ] Expand native candidate verification and implement the public `complete()`
      helper while retaining interactive screens as the behavioral authority.

## API and packaging

- [ ] Choose deep immutability or explicitly mutable nested mappings for Command
      and CommandTree; frozen dataclasses do not freeze their subcommands.
- [ ] Complete the remaining public shell/generator helpers or remove unused
      scaffolding from the API.
- [ ] Automate isolated wheel/sdist validation in CI, including runtime
      dependencies, console entrypoint behavior, and typed API distribution.
      The generate-only CLI has been smoke-tested in an isolated wheel installation.
- [ ] Test the declared Typer range and retain useful compatibility checks for
      its vendored internals. Decide whether the optional upstream Click
      comparison should have a provided dependency or be replaced.
- [ ] Defer PowerShell until native candidate behavior, descriptions, syntax, and
      Windows integration tests are implemented.
- [ ] Benchmark script size and completion latency on large/deep Typer apps;
      turn compatibility failures into small regression fixtures.
