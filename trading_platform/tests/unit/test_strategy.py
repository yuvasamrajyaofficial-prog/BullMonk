"""
Unit tests for strategy interface and dummy strategy implementation.

Tests that:
1. BaseStrategy interface can be implemented by a concrete dummy strategy.
2. Strategy lifecycle (initialize → on_bar → on_stop) works correctly.
3. Strategy emits signals to the EventBus.
4. Strategy is fully decoupled from broker implementations.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.clock import SimulatedClock
from core.enums import (
    AssetClass,
    EventType,
    Exchange,
    InstrumentType,
    Side,
    SignalType,
    StrategyState,
    Timeframe,
)
from core.events import EventBus, SignalEvent
from core.models import (
    Asset,
    OHLCVBar,
    Signal,
    StrategyConfig,
    StrategyMetadata,
)
from strategies.base import BaseStrategy


# ──────────────────────────────────────────────
# Dummy strategy for testing
# ──────────────────────────────────────────────

class AlwaysBuyStrategy(BaseStrategy):
    """
    Minimal test strategy that emits ENTER_LONG on every bar.

    This strategy has no broker knowledge. It simply proves
    that the BaseStrategy interface can be implemented and that
    signals flow correctly through the EventBus.
    """

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id=self._config.strategy_id,
            name="Always Buy",
            version="0.1.0",
            description="Test strategy — buys on every bar.",
            supported_asset_classes=[AssetClass.EQUITY],
            supported_timeframes=[Timeframe.D1],
        )

    def on_bar(self, bar: OHLCVBar) -> Optional[list[Signal]]:
        signal = Signal(
            strategy_id=self._config.strategy_id,
            asset=bar.asset,
            signal_type=SignalType.ENTER_LONG,
            strength=0.9,
            suggested_price=bar.close,
        )
        self._emit_signal(signal)
        return [signal]


class DoNothingStrategy(BaseStrategy):
    """Test strategy that never emits signals."""

    @property
    def metadata(self) -> StrategyMetadata:
        return StrategyMetadata(
            strategy_id=self._config.strategy_id,
            name="Do Nothing",
            version="0.1.0",
        )

    def on_bar(self, bar: OHLCVBar) -> Optional[list[Signal]]:
        return None


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def event_bus() -> EventBus:
    return EventBus()


@pytest.fixture
def clock() -> SimulatedClock:
    return SimulatedClock(start_time=datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc))


@pytest.fixture
def reliance_asset() -> Asset:
    return Asset(
        symbol="RELIANCE",
        exchange=Exchange.NSE,
        asset_class=AssetClass.EQUITY,
        instrument_type=InstrumentType.STOCK,
    )


@pytest.fixture
def config() -> StrategyConfig:
    return StrategyConfig(
        strategy_id="test-always-buy",
        parameters={},
        risk_per_trade_pct=1.0,
        max_open_positions=1,
    )


@pytest.fixture
def always_buy_strategy(
    config: StrategyConfig, clock: SimulatedClock, event_bus: EventBus
) -> AlwaysBuyStrategy:
    return AlwaysBuyStrategy(config=config, clock=clock, event_bus=event_bus)


@pytest.fixture
def sample_bar(reliance_asset: Asset) -> OHLCVBar:
    return OHLCVBar(
        asset=reliance_asset,
        timeframe=Timeframe.D1,
        timestamp=datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        open=Decimal("2900"),
        high=Decimal("3000"),
        low=Decimal("2850"),
        close=Decimal("2975"),
        volume=Decimal("1000000"),
    )


# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────

class TestStrategyInterface:
    def test_strategy_starts_in_initialized_state(
        self, always_buy_strategy: AlwaysBuyStrategy
    ):
        assert always_buy_strategy.state == StrategyState.INITIALIZED

    def test_initialize_transitions_to_running(
        self, always_buy_strategy: AlwaysBuyStrategy
    ):
        always_buy_strategy.initialize()
        assert always_buy_strategy.state == StrategyState.RUNNING

    def test_on_stop_transitions_to_stopped(
        self, always_buy_strategy: AlwaysBuyStrategy
    ):
        always_buy_strategy.initialize()
        always_buy_strategy.on_stop()
        assert always_buy_strategy.state == StrategyState.STOPPED

    def test_on_bar_emits_signal(
        self,
        always_buy_strategy: AlwaysBuyStrategy,
        sample_bar: OHLCVBar,
    ):
        received_signals = []

        def capture(event: SignalEvent):
            received_signals.append(event)

        always_buy_strategy._event_bus.subscribe(EventType.SIGNAL, capture)
        always_buy_strategy.initialize()
        result = always_buy_strategy.on_bar(sample_bar)

        assert result is not None
        assert len(result) == 1
        assert result[0].signal_type == SignalType.ENTER_LONG
        assert len(received_signals) == 1

    def test_signals_emitted_counter_increments(
        self,
        always_buy_strategy: AlwaysBuyStrategy,
        sample_bar: OHLCVBar,
    ):
        always_buy_strategy.initialize()
        assert always_buy_strategy.signals_emitted == 0
        always_buy_strategy.on_bar(sample_bar)
        always_buy_strategy.on_bar(sample_bar)
        assert always_buy_strategy.signals_emitted == 2

    def test_strategy_id_matches_config(
        self, always_buy_strategy: AlwaysBuyStrategy
    ):
        assert always_buy_strategy.strategy_id == "test-always-buy"

    def test_metadata_accessible(self, always_buy_strategy: AlwaysBuyStrategy):
        meta = always_buy_strategy.metadata
        assert meta.name == "Always Buy"
        assert AssetClass.EQUITY in meta.supported_asset_classes

    def test_do_nothing_strategy_returns_none(
        self,
        config: StrategyConfig,
        clock: SimulatedClock,
        event_bus: EventBus,
        sample_bar: OHLCVBar,
    ):
        config2 = StrategyConfig(
            strategy_id="do-nothing", parameters={}, max_open_positions=1
        )
        strategy = DoNothingStrategy(config=config2, clock=clock, event_bus=event_bus)
        strategy.initialize()
        result = strategy.on_bar(sample_bar)
        assert result is None

    def test_strategy_has_no_broker_dependency(self):
        """
        Verify no broker-specific imports exist in the strategy module.
        This is an architectural guard test.
        """
        import importlib
        import strategies.base as strategy_module
        import inspect

        source = inspect.getsource(strategy_module)
        forbidden_names = ["dhan", "zerodha", "binance", "upstox", "fyers", "kite"]
        for name in forbidden_names:
            assert name.lower() not in source.lower(), (
                f"Strategy base module must not reference broker '{name}'"
            )
