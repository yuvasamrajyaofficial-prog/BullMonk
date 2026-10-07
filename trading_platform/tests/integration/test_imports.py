"""
Integration test: project imports.

Tests that all public modules import cleanly without errors.
This is the top-level smoke test for the entire architecture.
"""

import importlib
import sys
import pytest


MODULES_TO_IMPORT = [
    "core",
    "core.enums",
    "core.models",
    "core.exceptions",
    "core.events",
    "core.clock",
    "config",
    "config.settings",
    "data",
    "data.interfaces",
    "data.models",
    "strategies",
    "strategies.base",
    "strategies.models",
    "execution",
    "execution.interfaces",
    "execution.models",
    "brokers",
    "brokers.base",
    "risk",
    "risk.manager",
    "portfolio",
    "portfolio.portfolio",
    "backtesting",
    "backtesting.engine",
    "analytics",
    "analytics.metrics",
    "logging_config",
]


@pytest.mark.parametrize("module_name", MODULES_TO_IMPORT)
def test_module_imports_cleanly(module_name: str):
    """Every listed module must import without raising any exception."""
    try:
        mod = importlib.import_module(module_name)
        assert mod is not None
    except ImportError as exc:
        pytest.fail(f"ImportError importing '{module_name}': {exc}")
    except Exception as exc:
        pytest.fail(f"Unexpected error importing '{module_name}': {exc}")
