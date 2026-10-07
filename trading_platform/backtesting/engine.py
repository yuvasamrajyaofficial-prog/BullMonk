"""
Backtesting Engine — Phase 1 Skeleton.

This module defines the BacktestEngine interface and a minimal
synchronous implementation that validates the architecture.

Full implementation (slippage models, commission, multi-asset,
walk-forward, Monte Carlo) will be built in subsequent phases.

Design principles:
- Deterministic: same data + same strategy = same result, always.
- Clock-driven: uses SimulatedClock — no wall-clock dependency.
- Event-based: reuses the same EventBus as live trading.
- No fabricated data: all data comes through HistoricalDataProvider.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional

from core.clock import SimulatedClock
from core.enums import Timeframe
from core.events import BarEvent, EventBus
from core.models import Asset, OHLCVBar, PortfolioSnapshot
from data.interfaces import HistoricalDataProvider
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Result model
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class BacktestResult:
    """Immutable summary of a completed backtest run."""

    strategy_id: str
    asset: Asset
    timeframe: Timeframe
    start_date: datetime
    end_date: datetime
    total_bars_processed: int
    total_signals: int
    total_trades: int
    net_pnl: Decimal = field(default=Decimal("0"))
    max_drawdown_pct: float = field(default=0.0)
    win_rate: float = field(default=0.0)
    snapshots: list[PortfolioSnapshot] = field(default_factory=list)


# ──────────────────────────────────────────────
# Abstract interface
# ──────────────────────────────────────────────

class BacktestEngine(ABC):
    """
    Abstract backtest engine interface.

    Decouples the backtest runner from any specific implementation
    (e.g. event-driven vs vectorised) so they can be swapped.
    """

    @abstractmethod
    def run(
        self,
        strategy: BaseStrategy,
        asset: Asset,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> BacktestResult:
        """
        Execute a backtest for the given strategy and time range.

        Args:
            strategy:  Initialised strategy instance.
            asset:     Instrument to backtest.
            timeframe: Bar resolution.
            start:     Inclusive start datetime (UTC).
            end:       Inclusive end datetime (UTC).

        Returns:
            BacktestResult with aggregated metrics.

        Raises:
            InsufficientDataError: If there are not enough bars.
            BacktestError:         On any other backtest failure.
        """


# ──────────────────────────────────────────────
# Minimal synchronous implementation
# ──────────────────────────────────────────────

class SimpleBacktestEngine(BacktestEngine):
    """
    Single-pass, bar-by-bar synchronous backtest engine.

    Phase 1 scope:
    - Iterates over historical bars in order.
    - Calls strategy.on_bar() for each bar.
    - Advances the SimulatedClock to each bar's timestamp.
    - Counts signals and bars.
    - Does NOT simulate order fills (that requires execution layer — Phase 2).

    This engine exists to validate the architecture end-to-end.
    """

    def __init__(
        self,
        data_provider: HistoricalDataProvider,
        event_bus: EventBus,
    ) -> None:
        """
        Args:
            data_provider: Source of historical OHLCV data.
            event_bus:     Shared event bus (same as used in live trading).
        """
        self._data_provider = data_provider
        self._event_bus = event_bus

    def run(
        self,
        strategy: BaseStrategy,
        asset: Asset,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
    ) -> BacktestResult:
        """Run the backtest. See BacktestEngine.run() for full docs."""
        logger.info(
            "BacktestEngine.run: strategy=%s asset=%s timeframe=%s start=%s end=%s",
            strategy.strategy_id,
            asset,
            timeframe.value,
            start.isoformat(),
            end.isoformat(),
        )

        bars: list[OHLCVBar] = self._data_provider.get_bars(
            asset, timeframe, start, end
        )

        if not bars:
            from core.exceptions import InsufficientDataError
            raise InsufficientDataError(
                symbol=asset.symbol, required_bars=1, available_bars=0
            )

        clock = SimulatedClock(start_time=bars[0].timestamp)
        total_signals = 0
        bars_processed = 0

        strategy.initialize()

        for bar in bars:
            # Advance simulated clock to this bar's timestamp
            clock.set_time(bar.timestamp)

            # Publish bar event to the bus
            self._event_bus.publish(
                BarEvent(
                    source="BacktestEngine",
                    payload={"bar": bar.model_dump(mode="json")},
                )
            )

            # Let the strategy process the bar
            signals = strategy.on_bar(bar)
            if signals:
                total_signals += len(signals)
                for signal in signals:
                    strategy._emit_signal(signal)

            bars_processed += 1

        strategy.on_stop()

        result = BacktestResult(
            strategy_id=strategy.strategy_id,
            asset=asset,
            timeframe=timeframe,
            start_date=start,
            end_date=end,
            total_bars_processed=bars_processed,
            total_signals=total_signals,
            total_trades=0,  # Phase 1 — execution not yet wired
        )

        logger.info(
            "BacktestEngine.run complete: bars=%d signals=%d",
            bars_processed,
            total_signals,
        )
        return result
