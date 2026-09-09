"""Built-in generators and the registry that resolves shells to them."""

from __future__ import annotations

from collections.abc import Iterator

from ..config import GenerationOptions
from ..shells import Shell, ShellName
from .base import Generator


def get_generator(
    shell: ShellName, options: GenerationOptions | None = None
) -> Generator:
    """Instantiate the generator registered for ``shell``.

    Raises:
        UnsupportedShellError: if nothing is registered for ``shell``.
    """
    raise NotImplementedError


def register(generator: type[Generator], *, override: bool = False) -> type[Generator]:
    """Register a generator, keyed on its ``shell`` attribute.

    Usable as a decorator. Lets a project add a shell (nushell, elvish, xonsh)
    or replace a built-in one without forking.

    Raises:
        ValueError: if ``shell`` is already registered and ``override`` is False.
    """
    raise NotImplementedError


def available_shells() -> Iterator[Shell]:
    """Yield every registered shell, built-in and third-party."""
    raise NotImplementedError


__all__ = [
    "Generator",
    "available_shells",
    "get_generator",
    "register",
]
