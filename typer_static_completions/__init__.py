"""Generate static shell completions for typer applications.

Typer's built-in completion is *dynamic*: the script installed by
``--install-completion`` re-executes your program on every TAB press to ask what
the candidates are. That costs a Python interpreter startup per completion, which
is seconds on a CLI with heavy transitive imports.

This library bakes the command names, option flags and enum choices into plain
shell code. Static candidates do not start Python; delegated dynamic parameters
still invoke the app. This API is currently a scaffold, not an implementation.

    >>> from typer_static_completions import generate
    >>> from myapp.cli import app
    >>> print(generate(app, "myapp", "fish"))

The trade-off is that a generated script is a snapshot and can drift from the
app. Use :class:`CompletionSet` to check committed scripts in CI, the same way
you would check a lockfile.

What can and cannot be baked in:

===================================  ========================================
Static                               Needs the app at runtime
===================================  ========================================
Command and subcommand names         ``autocompletion=`` callbacks
Option flags, incl. ``--no-x``       Completions depending on ``ctx``
``Enum`` choices                     Plugins discovered only at runtime
Help texts                           Anything reading the filesystem or net
File fallback for ``Path`` params
===================================  ========================================

For the runtime column, :class:`DynamicPolicy` lets you keep dynamic completion
for just those parameters, so only they pay the interpreter startup.
"""

from __future__ import annotations

import importlib.metadata
import warnings

from .config import DynamicPolicy, GenerationOptions
from .core import CheckResult, CompletionSet, SyncResult, generate, write
from .errors import (
    AppLoadError,
    IntrospectionError,
    ScriptSyntaxError,
    ShellUnavailableError,
    StaleCompletionsError,
    StaticCompletionError,
    UnsupportedShellError,
)
from .introspect import from_app, from_command
from .model import Command, CommandTree, Param, ParamKind, ValueKind
from .shells import DEFAULT_SHELLS, Shell

try:
    __version__ = importlib.metadata.version(__name__)
except importlib.metadata.PackageNotFoundError as e:  # pragma: no cover
    warnings.warn(f"Could not determine version of {__name__}\n{e!s}", stacklevel=2)
    __version__ = "unknown"

__all__ = [
    "DEFAULT_SHELLS",
    # errors
    "AppLoadError",
    "CheckResult",
    # model
    "Command",
    "CommandTree",
    # core
    "CompletionSet",
    # config
    "DynamicPolicy",
    "GenerationOptions",
    "IntrospectionError",
    "Param",
    "ParamKind",
    "ScriptSyntaxError",
    "Shell",
    "ShellUnavailableError",
    "StaleCompletionsError",
    "StaticCompletionError",
    "SyncResult",
    "UnsupportedShellError",
    "ValueKind",
    "__version__",
    "from_app",
    "from_command",
    "generate",
    "write",
]
