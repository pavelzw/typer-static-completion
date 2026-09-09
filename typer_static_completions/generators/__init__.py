"""Built-in generators and the registry that resolves shells to them."""

from __future__ import annotations

from collections.abc import Iterator

from ..config import GenerationOptions
from ..errors import UnsupportedShellError
from ..shells import ShellName
from .base import Generator
from .bash import BashGenerator
from .fish import FishGenerator
from .zsh import ZshGenerator

_REGISTRY: dict[str, type[Generator]] = {
    "bash": BashGenerator,
    "fish": FishGenerator,
    "zsh": ZshGenerator,
}


def get_generator(
    shell: ShellName, options: GenerationOptions | None = None
) -> Generator:
    """Instantiate the generator registered for ``shell``.

    Raises:
        UnsupportedShellError: if nothing is registered for ``shell``.
    """
    try:
        return _REGISTRY[shell](options)
    except KeyError as exc:
        raise UnsupportedShellError(f"No implemented generator for {shell!r}") from exc


def register(generator: type[Generator], *, override: bool = False) -> type[Generator]:
    """Register a generator, keyed on its ``shell`` attribute.

    Usable as a decorator. Lets a project add a shell (nushell, elvish, xonsh)
    or replace a built-in one without forking.

    Raises:
        ValueError: if ``shell`` is already registered and ``override`` is False.
    """
    if generator.shell in _REGISTRY and not override:
        raise ValueError(f"Generator already registered for {generator.shell!r}")
    _REGISTRY[generator.shell] = generator
    return generator


def available_shells() -> Iterator[str]:
    """Yield every registered shell, built-in and third-party."""
    return iter(_REGISTRY)


__all__ = [
    "Generator",
    "available_shells",
    "get_generator",
    "register",
]
