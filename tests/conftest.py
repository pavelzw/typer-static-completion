"""Ensure the dedicated integration job cannot silently skip its dependencies."""

import importlib
import shutil

import pytest

pytest.register_assert_rewrite("snapshot_assertions")


def pytest_addoption(parser):
    parser.addoption("--require-snapshots", action="store_true", default=False)


def pytest_configure(config):
    if config.getoption("--require-snapshots"):
        for module in ("pexpect", "pyte"):
            try:
                importlib.import_module(module)
            except ImportError as exc:
                raise pytest.UsageError(
                    f"Snapshot dependency missing: {module}"
                ) from exc
        for shell in ("bash", "fish", "zsh"):
            if not shutil.which(shell):
                raise pytest.UsageError(f"{shell} is required for screen snapshots")
