"""
Opening Range Breakout (ORB) Strategy for Indian Markets (NSE).

Logic:
- Establishes the Opening Range high and low during the initial session window (e.g. 09:15 - 09:45 IST).
- Emits ENTER_LONG on a break above the opening high.
- Emits ENTER_SHORT on a break below the opening low.
- Enforces an intraday square-off exit rule at 15:15 IST.
"""

from __future__ import annotations

from datetime import datetime, time, timezone
from decimal import Decimal
from typing import Optional
from zoneinfo import ZoneInfo

from core.clock import Clock, SimulatedClock
from core.enums import SignalType
from core.events import EventBus
from core.models import OHLCVBar, Signal, StrategyConfig, StrategyMetadata
from strategies.base import BaseStrategy

IST = ZoneInfo("Asia/Kolkata")


class OpeningRangeBreakoutStrategy(BaseStrategy):
    """Opening Range Breakout intraday trading strategy."""

    def __init__(
        self,
        config: Optional[StrategyConfig] = None,
        clock: Optional[Clock] = None,
        event_bus: Optional[EventBus] = None,
        orb_minutes: int = 30,
        trade_quantity: Decimal = Decimal("50"),
    ) -> None:
        cfg = config or StrategyConfig(
            strategy_id="STRAT-NIFTY-ORB",
            parameters={"orb_minutes": orb_minutes},
            risk_per_trade_pct=1.0,
        )
        clk = clock or SimulatedClock(start_time=datetime(2025, 1, 1, tzinfo=timezone.utc))
        bus = event_bus or EventBus()
        super().__init__(config=cfg, clock=clk, event_bus=bus)

        self._metadata = StrategyMetadata(
            strategy_id=cfg.strategy_id,
            name="NIFTY Opening Range Breakout (ORB)",
            version="1.0.0",
            author="BullMonk Quant Systems",
            description="Systematic breakout from the initial session range with strict session exit.",
        )
        self.orb_minutes = orb_minutes
        self.trade_quantity = trade_quantity

        self._current_date = None
        self._orb_high: Optional[Decimal] = None
        self._orb_low: Optional[Decimal] = None
        self._orb_formed: bool = False
        self._in_position: bool = False

    @property
    def metadata(self) -> StrategyMetadata:
        return self._metadata

    def on_bar(self, bar: OHLCVBar) -> list[Signal]:
        bar_ist = bar.timestamp.astimezone(IST)
        bar_date = bar_ist.date()
        bar_time = bar_ist.time()

        signals: list[Signal] = []

        # Reset on new trading day
        if self._current_date != bar_date:
            self._current_date = bar_date
            self._orb_high = None
            self._orb_low = None
            self._orb_formed = False
            self._in_position = False

        # Session Square-off window (15:15 IST)
        if bar_time >= time(15, 15):
            if self._in_position:
                sig = Signal(
                    strategy_id=self.strategy_id,
                    asset=bar.asset,
                    signal_type=SignalType.EXIT_LONG,
                    suggested_quantity=self.trade_quantity,
                    strength=1.0,
                    timestamp=bar.timestamp,
                )
                signals.append(sig)
                self._in_position = False
            return signals

        # 09:15 to 09:45 IST: Form opening range
        if bar_time < time(9, 45):
            if self._orb_high is None or bar.high > self._orb_high:
                self._orb_high = bar.high
            if self._orb_low is None or bar.low < self._orb_low:
                self._orb_low = bar.low
            return signals

        # After 09:45 IST: Breakout evaluation
        self._orb_formed = True

        if not self._in_position and self._orb_high is not None and self._orb_low is not None:
            # Bullish Breakout
            if bar.close > self._orb_high:
                sig = Signal(
                    strategy_id=self.strategy_id,
                    asset=bar.asset,
                    signal_type=SignalType.ENTER_LONG,
                    suggested_quantity=self.trade_quantity,
                    strength=0.92,
                    timestamp=bar.timestamp,
                )
                signals.append(sig)
                self._in_position = True

            # Bearish Breakdown
            elif bar.close < self._orb_low:
                sig = Signal(
                    strategy_id=self.strategy_id,
                    asset=bar.asset,
                    signal_type=SignalType.ENTER_SHORT,
                    suggested_quantity=self.trade_quantity,
                    strength=0.92,
                    timestamp=bar.timestamp,
                )
                signals.append(sig)
                self._in_position = True

        return signals
