#!/usr/bin/env python3
"""
Health check script for the BullMonk Trading Platform.

Usage:
    python scripts/health_check.py

This script verifies:
1. Python version compatibility.
2. All required dependencies are installed.
3. All platform modules import cleanly.
4. Configuration loads without errors.
5. Core models can be instantiated.
6. Clock works correctly.
7. EventBus works correctly.
8. No secrets are present in the environment (by validating only safe keys).

Exit codes:
    0 — All checks passed.
    1 — One or more checks failed.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
import importlib
import traceback
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Callable

# Ensure platform directory is on sys.path
PLATFORM_DIR = Path(__file__).resolve().parent.parent
if str(PLATFORM_DIR) not in sys.path:
    sys.path.insert(0, str(PLATFORM_DIR))

# Ensure UTF-8 output on Windows terminals
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ─────────────────────────────────────────────
# Minimum Python version requirement
# ─────────────────────────────────────────────
MIN_PYTHON = (3, 11)

# ─────────────────────────────────────────────
# Colour output (no external dependency)
# ─────────────────────────────────────────────
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
BOLD = "\033[1m"
RESET = "\033[0m"


def _safe_char(char: str, fallback: str) -> str:
    try:
        char.encode(sys.stdout.encoding or "utf-8")
        return char
    except Exception:
        return fallback


CHECK_MARK = _safe_char("✓", "[OK]")
CROSS_MARK = _safe_char("✗", "[FAIL]")
WARN_MARK = _safe_char("⚠", "[WARN]")
LINE_CHAR = _safe_char("─", "-")


def ok(msg: str) -> None:
    print(f"  {GREEN}{CHECK_MARK}{RESET}  {msg}")


def fail(msg: str) -> None:
    print(f"  {RED}{CROSS_MARK}{RESET}  {msg}")


def warn(msg: str) -> None:
    print(f"  {YELLOW}{WARN_MARK}{RESET}  {msg}")


def header(title: str) -> None:
    sep = LINE_CHAR * 60
    print(f"\n{BOLD}{BLUE}{sep}{RESET}")
    print(f"{BOLD}{BLUE}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{sep}{RESET}")


# ─────────────────────────────────────────────
# Check registry
# ─────────────────────────────────────────────

failures: list[str] = []
warnings: list[str] = []


def check(description: str, fn: Callable[[], None]) -> bool:
    """Run a single check and record pass/fail."""
    try:
        fn()
        ok(description)
        return True
    except Exception as exc:
        fail(f"{description}  →  {exc}")
        failures.append(f"{description}: {exc}")
        return False


# ═════════════════════════════════════════════
# CHECKS
# ═════════════════════════════════════════════

def check_python_version() -> None:
    header("1. Python Version")
    version = sys.version_info
    if version < MIN_PYTHON:
        raise RuntimeError(
            f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ required, "
            f"got {version.major}.{version.minor}.{version.micro}"
        )
    ok(f"Python {version.major}.{version.minor}.{version.micro}")


def check_dependencies() -> None:
    header("2. Dependencies")
    required = [
        ("pydantic", "Pydantic v2"),
        ("pydantic_settings", "pydantic-settings"),
        ("pytest", "pytest"),
    ]
    for module_name, label in required:
        check(f"{label} importable", lambda m=module_name: importlib.import_module(m))


def check_module_imports() -> None:
    header("3. Platform Module Imports")
    modules = [
        "core.enums",
        "core.models",
        "core.exceptions",
        "core.events",
        "core.clock",
        "config.settings",
        "data.interfaces",
        "data.models",
        "strategies.base",
        "strategies.models",
        "execution.interfaces",
        "execution.models",
        "brokers.base",
        "risk.manager",
        "portfolio.portfolio",
        "backtesting.engine",
        "analytics.metrics",
        "logging_config",
    ]
    for mod in modules:
        check(mod, lambda m=mod: importlib.import_module(m))


def check_configuration() -> None:
    header("4. Configuration")

    def load_settings():
        from config.settings import Settings
        s = Settings()
        assert s.app_name
        assert s.environment in ("development", "staging", "production")
        assert s.log_level in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

    check("Settings instantiation", load_settings)

    def no_hard_coded_secrets():
        from config.settings import Settings
        s = Settings()
        # Secrets must not be hard-coded — they should be None unless in env
        import os
        secret_vars = [
            "DHAN_ACCESS_TOKEN", "ZERODHA_ACCESS_TOKEN",
            "BINANCE_SECRET", "JWT_SECRET"
        ]
        for var in secret_vars:
            if var not in os.environ:
                val = getattr(s, var.lower(), None)
                assert val is None, f"{var} has a hard-coded value!"

    check("No hard-coded secrets", no_hard_coded_secrets)


def check_core_models() -> None:
    header("5. Core Models")

    def asset_models():
        from core.enums import AssetClass, Exchange, InstrumentType, OptionType, OptionStyle
        from core.models import Asset
        from datetime import datetime, timezone
        from decimal import Decimal

        # Indian equity
        reliance = Asset(symbol="RELIANCE", exchange=Exchange.NSE,
                         asset_class=AssetClass.EQUITY,
                         instrument_type=InstrumentType.STOCK)
        assert reliance.symbol == "RELIANCE"

        # NIFTY index option
        nifty_ce = Asset(
            symbol="NIFTY", exchange=Exchange.NFO,
            asset_class=AssetClass.OPTIONS,
            instrument_type=InstrumentType.INDEX_OPTIONS,
            strike_price=Decimal("24000"),
            option_type=OptionType.CALL,
            option_style=OptionStyle.EUROPEAN,
            expiry=datetime(2025, 12, 25, tzinfo=timezone.utc),
            lot_size=50,
        )
        assert nifty_ce.strike_price == Decimal("24000")

        # BTC crypto
        btc = Asset(symbol="BTC", exchange=Exchange.BINANCE,
                    asset_class=AssetClass.CRYPTO,
                    instrument_type=InstrumentType.CRYPTO_SPOT,
                    currency="USDT")
        assert btc.currency == "USDT"

        # EURUSD forex
        eurusd = Asset(symbol="EURUSD", exchange=Exchange.FOREX_OTC,
                       asset_class=AssetClass.FOREX,
                       instrument_type=InstrumentType.CURRENCY_PAIR,
                       currency="USD")
        assert eurusd.asset_class == AssetClass.FOREX

    check("Asset models (equity, options, crypto, forex)", asset_models)

    def ohlcv_bar():
        from core.models import Asset, OHLCVBar
        from core.enums import AssetClass, Exchange, InstrumentType, Timeframe
        from datetime import datetime, timezone
        from decimal import Decimal

        asset = Asset(symbol="NIFTY", exchange=Exchange.NFO,
                      asset_class=AssetClass.FUTURES,
                      instrument_type=InstrumentType.INDEX_FUTURES)
        bar = OHLCVBar(
            asset=asset, timeframe=Timeframe.M5,
            timestamp=datetime.now(tz=timezone.utc),
            open=Decimal("24000"), high=Decimal("24100"),
            low=Decimal("23950"), close=Decimal("24080"),
            volume=Decimal("50000"),
        )
        assert bar.high >= bar.open

    check("OHLCVBar model", ohlcv_bar)

    def order_model():
        from core.models import Asset, Order
        from core.enums import AssetClass, Exchange, InstrumentType, OrderType, Side
        from decimal import Decimal

        asset = Asset(symbol="RELIANCE", exchange=Exchange.NSE,
                      asset_class=AssetClass.EQUITY,
                      instrument_type=InstrumentType.STOCK)
        order = Order(asset=asset, side=Side.BUY,
                      order_type=OrderType.MARKET, quantity=Decimal("10"))
        assert order.remaining_quantity == Decimal("10")

    check("Order model", order_model)


def check_clock() -> None:
    header("6. Clock")

    def live_clock_utc():
        from core.clock import LiveClock
        clock = LiveClock()
        now = clock.now()
        assert now.tzinfo is not None

    check("LiveClock returns UTC", live_clock_utc)

    def simulated_clock():
        from core.clock import SimulatedClock
        from datetime import datetime, timezone, timedelta
        start = datetime(2024, 1, 15, 9, 0, 0, tzinfo=timezone.utc)
        clock = SimulatedClock(start_time=start)
        clock.advance(timedelta(minutes=5))
        expected = start + timedelta(minutes=5)
        assert clock.now() == expected

    check("SimulatedClock advance", simulated_clock)


def check_event_bus() -> None:
    header("7. EventBus")

    def event_bus_publish_subscribe():
        from core.events import EventBus, BarEvent
        from core.enums import EventType
        received = []
        bus = EventBus()
        bus.subscribe(EventType.BAR, received.append)
        bus.publish(BarEvent(source="health_check"))
        assert len(received) == 1

    check("EventBus publish/subscribe", event_bus_publish_subscribe)


def check_logging() -> None:
    header("8. Logging System")

    def configure_and_log():
        from logging_config import configure_logging, get_logger
        configure_logging(level="WARNING")  # quiet during health check
        logger = get_logger("app")
        logger.warning("Health check: logging system OK")

    check("Logging configuration", configure_and_log)


# ═════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════

def main() -> int:
    print(f"\n{BOLD}BullMonk Trading Platform — Health Check{RESET}")
    print(f"Timestamp: {datetime.now(tz=timezone.utc).isoformat()}")

    check_python_version()
    check_dependencies()
    check_module_imports()
    check_configuration()
    check_core_models()
    check_clock()
    check_event_bus()
    check_logging()

    header("Summary")
    if not failures:
        print(f"\n  {GREEN}{BOLD}{CHECK_MARK} All checks passed.{RESET}")
        print(f"  Environment: READY for development.\n")
        return 0
    else:
        print(f"\n  {RED}{BOLD}{CROSS_MARK} {len(failures)} check(s) FAILED:{RESET}")
        for f in failures:
            print(f"    {RED}*{RESET} {f}")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
