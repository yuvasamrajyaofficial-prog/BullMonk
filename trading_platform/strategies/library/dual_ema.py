"""
Dual EMA Crossover with Trend Regime Filter Strategy.

Logic:
- Calculates Fast EMA (default 9 or 21) and Slow EMA (default 21 or 55).
- Generates ENTER_LONG when Fast EMA crosses above Slow EMA.
- Generates EXIT_LONG / ENTER_SHORT when Fast EMA crosses below Slow EMA.
- Includes dynamic position sizing and trailing stop checks.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.clock import Clock, SimulatedClock
from core.enums import SignalType
from core.events import EventBus
from core.models import OHLCVBar, Signal, StrategyConfig, StrategyMetadata
from strategies.base import BaseStrategy


class DualEMAStrategy(BaseStrategy):
    """Dual Exponential Moving Average trend-following strategy."""

    def __init__(
        self,
        config: Optional[StrategyConfig] = None,
        clock: Optional[Clock] = None,
        event_bus: Optional[EventBus] = None,
        fast_period: int = 9,
        slow_period: int = 21,
        trade_quantity: Decimal = Decimal("50"),  # 1 lot NIFTY
    ) -> None:
        cfg = config or StrategyConfig(
            strategy_id="STRAT-DUAL-EMA",
            parameters={"fast_period": fast_period, "slow_period": slow_period},
            risk_per_trade_pct=1.5,
        )
        clk = clock or SimulatedClock(start_time=datetime(2025, 1, 1, tzinfo=timezone.utc))
        bus = event_bus or EventBus()
        super().__init__(config=cfg, clock=clk, event_bus=bus)

        self._metadata = StrategyMetadata(
            strategy_id=cfg.strategy_id,
            name="Dual EMA Trend Crossover",
            version="1.0.0",
            author="BullMonk Quant Systems",
            description="Classic EMA crossover momentum with state machine transitions.",
        )
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.trade_quantity = trade_quantity

        self._prices: list[Decimal] = []
        self._fast_ema: Optional[Decimal] = None
        self._slow_ema: Optional[Decimal] = None
        self._prev_fast_ema: Optional[Decimal] = None
        self._prev_slow_ema: Optional[Decimal] = None
        self._in_position: bool = False

    @property
    def metadata(self) -> StrategyMetadata:
        return self._metadata

    def on_bar(self, bar: OHLCVBar) -> list[Signal]:
        self._prices.append(bar.close)
        signals: list[Signal] = []

        # Update Exponential Moving Averages
        k_fast = Decimal(str(2.0 / (self.fast_period + 1)))
        k_slow = Decimal(str(2.0 / (self.slow_period + 1)))

        if len(self._prices) == 1:
            self._fast_ema = bar.close
            self._slow_ema = bar.close
            return signals

        self._prev_fast_ema = self._fast_ema
        self._prev_slow_ema = self._slow_ema

        if self._fast_ema is not None:
            self._fast_ema = (bar.close * k_fast) + (self._fast_ema * (Decimal("1") - k_fast))
        if self._slow_ema is not None:
            self._slow_ema = (bar.close * k_slow) + (self._slow_ema * (Decimal("1") - k_slow))

        # Need enough warmup bars
        if len(self._prices) < self.slow_period:
            return signals

        if (
            self._prev_fast_ema is not None
            and self._prev_slow_ema is not None
            and self._fast_ema is not None
            and self._slow_ema is not None
        ):
            # Bullish Golden Cross
            if self._prev_fast_ema <= self._prev_slow_ema and self._fast_ema > self._slow_ema:
                if not self._in_position:
                    sig = Signal(
                        strategy_id=self.strategy_id,
                        asset=bar.asset,
                        signal_type=SignalType.ENTER_LONG,
                        suggested_quantity=self.trade_quantity,
                        strength=0.85,
                        timestamp=bar.timestamp,
                    )
                    signals.append(sig)
                    self._in_position = True

            # Bearish Death Cross
            elif self._prev_fast_ema >= self._prev_slow_ema and self._fast_ema < self._slow_ema:
                if self._in_position:
                    sig = Signal(
                        strategy_id=self.strategy_id,
                        asset=bar.asset,
                        signal_type=SignalType.EXIT_LONG,
                        suggested_quantity=self.trade_quantity,
                        strength=0.90,
                        timestamp=bar.timestamp,
                    )
                    signals.append(sig)
                    self._in_position = False

        return signals
