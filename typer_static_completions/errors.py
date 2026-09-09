"""Exception hierarchy for typer-static-completions."""

from __future__ import annotations


class StaticCompletionError(Exception):
    """Base class for every error raised by this library."""


class UnsupportedShellError(StaticCompletionError):
    """No generator is registered for the requested shell."""


class AppLoadError(StaticCompletionError):
    """A ``"module:attribute"`` target could not be imported, or is not an app."""


class IntrospectionError(StaticCompletionError):
    """The command tree could not be read.

    Usually a typer version whose internals this library does not know about.
    """


class StaleCompletionsError(StaticCompletionError):
    """Committed completion scripts do not match the current app.

    Raised by :meth:`typer_static_completions.CheckResult.raise_for_status`.
    """


class ShellUnavailableError(StaticCompletionError):
    """A shell binary needed to verify a generated script is not installed."""


class ScriptSyntaxError(StaticCompletionError):
    """A generated script was rejected by the shell's own parser."""
