"""
Bollinger Bands Mean Reversion Strategy.

Logic:
- Calculates 20-period Simple Moving Average and 2.0 standard deviation bands.
- Enters Long when price bounces off Lower Band.
- Enters Short when price rejects Upper Band.
- Exits when price mean-reverts to the Middle Band (SMA).
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import math
from typing import Optional

from core.clock import Clock, SimulatedClock
from core.enums import SignalType
from core.events import EventBus
from core.models import OHLCVBar, Signal, StrategyConfig, StrategyMetadata
from strategies.base import BaseStrategy


class BollingerReversionStrategy(BaseStrategy):
    """Bollinger Bands Statistical Mean Reversion Strategy."""

    def __init__(
        self,
        config: Optional[StrategyConfig] = None,
        clock: Optional[Clock] = None,
        event_bus: Optional[EventBus] = None,
        period: int = 20,
        num_std: float = 2.0,
        trade_quantity: Decimal = Decimal("50"),
    ) -> None:
        cfg = config or StrategyConfig(
            strategy_id="STRAT-BOLLINGER-REV",
            parameters={"period": period, "num_std": num_std},
            risk_per_trade_pct=1.0,
        )
        clk = clock or SimulatedClock(start_time=datetime(2025, 1, 1, tzinfo=timezone.utc))
        bus = event_bus or EventBus()
        super().__init__(config=cfg, clock=clk, event_bus=bus)

        self._metadata = StrategyMetadata(
            strategy_id=cfg.strategy_id,
            name="Bollinger Bands Mean Reversion",
            version="1.0.0",
            author="BullMonk Quant Systems",
            description="Statistical mean reversion with dynamic volatility bands.",
        )
        self.period = period
        self.num_std = num_std
        self.trade_quantity = trade_quantity

        self._closes: list[Decimal] = []
        self._position: Optional[str] = None  # None | "LONG" | "SHORT"

    @property
    def metadata(self) -> StrategyMetadata:
        return self._metadata

    def on_bar(self, bar: OHLCVBar) -> list[Signal]:
        self._closes.append(bar.close)
        signals: list[Signal] = []

        if len(self._closes) < self.period:
            return signals

        # Calculate SMA and Standard Deviation over last N closes
        window = [float(c) for c in self._closes[-self.period:]]
        mean_val = sum(window) / self.period
        variance = sum((x - mean_val) ** 2 for x in window) / self.period
        std_dev = math.sqrt(variance)

        upper_band = Decimal(str(round(mean_val + (self.num_std * std_dev), 2)))
        lower_band = Decimal(str(round(mean_val - (self.num_std * std_dev), 2)))
        middle_band = Decimal(str(round(mean_val, 2)))

        curr_close = bar.close

        # Entry logic
        if self._position is None:
            if curr_close <= lower_band:
                sig = Signal(
                    strategy_id=self.strategy_id,
                    asset=bar.asset,
                    signal_type=SignalType.ENTER_LONG,
                    suggested_quantity=self.trade_quantity,
                    strength=0.88,
                    timestamp=bar.timestamp,
                )
                signals.append(sig)
                self._position = "LONG"

            elif curr_close >= upper_band:
                sig = Signal(
                    strategy_id=self.strategy_id,
                    asset=bar.asset,
                    signal_type=SignalType.ENTER_SHORT,
                    suggested_quantity=self.trade_quantity,
                    strength=0.88,
                    timestamp=bar.timestamp,
                )
                signals.append(sig)
                self._position = "SHORT"

        # Exit on mean reversion to middle band
        elif self._position == "LONG" and curr_close >= middle_band:
            sig = Signal(
                strategy_id=self.strategy_id,
                asset=bar.asset,
                signal_type=SignalType.EXIT_LONG,
                suggested_quantity=self.trade_quantity,
                strength=0.75,
                timestamp=bar.timestamp,
            )
            signals.append(sig)
            self._position = None

        elif self._position == "SHORT" and curr_close <= middle_band:
            sig = Signal(
                strategy_id=self.strategy_id,
                asset=bar.asset,
                signal_type=SignalType.EXIT_SHORT,
                suggested_quantity=self.trade_quantity,
                strength=0.75,
                timestamp=bar.timestamp,
            )
            signals.append(sig)
            self._position = None

        return signals
