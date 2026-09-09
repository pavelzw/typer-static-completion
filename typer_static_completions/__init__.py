"""Generate static shell completions for typer applications.

Typer's built-in completion is *dynamic*: the script installed by
``--install-completion`` re-executes your program on every TAB press to ask what
the candidates are. That costs a Python interpreter startup per completion, which
is seconds on a CLI with heavy transitive imports.

This library bakes the command names, option flags and enum choices into plain
shell code. Static candidates do not start Python; delegated dynamic parameters
would invoke the app. Bash, Fish, and Zsh generation are implemented; PowerShell and delegated
callbacks are not yet implemented. Dynamic values are omitted by default.

    >>> from typer_static_completions import generate
    >>> from myapp.cli import app
    >>> print(generate(app, "myapp", "bash"))

The trade-off is that a generated script is a snapshot and can drift from the
app. Regenerate scripts when the command tree changes.

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

For the runtime column, :class:`DynamicPolicy` controls omission, file fallback,
or generation errors. Hybrid delegation is reserved for a future implementation.
"""

from __future__ import annotations

import importlib.metadata
import warnings

from .config import DynamicPolicy, GenerationOptions
from .core import generate, write
from .errors import (
    AppLoadError,
    IntrospectionError,
    ScriptSyntaxError,
    ShellUnavailableError,
    StaticCompletionError,
    UnsupportedShellError,
)
from .introspect import from_app, from_command
from .model import Command, CommandTree, Param, ParamKind, ValueKind, ValueSpec
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
    # model
    "Command",
    "CommandTree",
    # core
    # config
    "DynamicPolicy",
    "GenerationOptions",
    "IntrospectionError",
    "Param",
    "ParamKind",
    "ScriptSyntaxError",
    "Shell",
    "ShellUnavailableError",
    "StaticCompletionError",
    "UnsupportedShellError",
    "ValueKind",
    "ValueSpec",
    "__version__",
    "from_app",
    "from_command",
    "generate",
    "write",
]
