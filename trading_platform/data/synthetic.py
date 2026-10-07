"""
Deterministic synthetic OHLCV market data generator for testing and research.

Generates realistic price action using Geometric Brownian Motion (GBM)
with micro-step path generation to ensure mathematically valid OHLC relationships:
- High >= max(Open, Close)
- Low <= min(Open, Close)
- Low <= High
- Volume >= 0
- No impossible candles
- Realistic intraday U-shaped volume curve
- Strict adherence to exchange session calendars
- Explicitly flags all generated bars with DataSource.SYNTHETIC
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from core.enums import DataSource, Timeframe
from core.models import Asset, OHLCVBar
from data.nifty import create_nifty_index
from data.sessions import NSESessionCalendar, SessionCalendar, _timeframe_to_timedelta


@dataclass
class SyntheticDataConfig:
    """Configuration parameters for deterministic synthetic data generation."""

    asset: Optional[Asset] = None
    start_price: Decimal = Decimal("24000.00")
    volatility: float = 0.16           # Annualized volatility (e.g. 16%)
    drift: float = 0.08                # Annualized drift (e.g. +8%)
    base_volume: Decimal = Decimal("50000")
    volume_dispersion: float = 0.35    # Log-normal standard deviation for volume
    session_calendar: Optional[SessionCalendar] = None
    number_of_sessions: int = 5        # Number of consecutive trading days
    timeframe: Timeframe = Timeframe.M5
    seed: Optional[int] = 42           # Random seed for determinism
    start_date: Optional[date] = None  # Start trading day (defaults to recent Monday)
    micro_steps_per_bar: int = 6       # Intra-bar ticks simulated for realistic wicks

    def __post_init__(self) -> None:
        if self.asset is None:
            self.asset = create_nifty_index()
        if self.session_calendar is None:
            self.session_calendar = NSESessionCalendar()
        if self.start_date is None:
            # Default to a recent stable Monday
            self.start_date = date(2025, 1, 6)
        if self.start_price <= 0:
            raise ValueError("start_price must be positive")
        if self.volatility < 0:
            raise ValueError("volatility must be non-negative")
        if self.base_volume < 0:
            raise ValueError("base_volume must be non-negative")
        if self.number_of_sessions <= 0:
            raise ValueError("number_of_sessions must be >= 1")


class SyntheticOHLCVGenerator:
    """
    Deterministic OHLCV bar generator.
    Guarantees reproducible, mathematically sound candlesticks.
    """

    # Annual trading days convention for Indian markets
    ANNUAL_TRADING_DAYS = 250.0
    NSE_SESSION_HOURS = 6.25  # 09:15 to 15:30 = 6 hours 15 minutes

    def __init__(self, seed: Optional[int] = 42) -> None:
        self._seed = seed
        self._rng = random.Random(seed)

    def set_seed(self, seed: Optional[int]) -> None:
        """Reset the internal pseudo-random number generator seed."""
        self._seed = seed
        self._rng = random.Random(seed)

    def generate(self, config: Optional[SyntheticDataConfig] = None) -> list[OHLCVBar]:
        """
        Generate synthetic historical bars matching the configuration.

        Returns:
            List of valid OHLCVBar instances with DataSource.SYNTHETIC in ascending chronological order.
        """
        cfg = config or SyntheticDataConfig()
        if cfg.seed is not None:
            self.set_seed(cfg.seed)

        cal = cfg.session_calendar or NSESessionCalendar()
        step = _timeframe_to_timedelta(cfg.timeframe)
        step_seconds = step.total_seconds()

        # Collect trading days
        trading_days: list[date] = []
        curr_date = cfg.start_date or date(2025, 1, 6)
        while len(trading_days) < cfg.number_of_sessions:
            if cal.is_trading_day(curr_date):
                trading_days.append(curr_date)
            curr_date += timedelta(days=1)

        # Get session intervals
        session_intervals: list[tuple[datetime, datetime]] = []
        for td in trading_days:
            session_intervals.extend(cal.get_trading_intervals(td, td))

        # Time fraction dt for each micro step
        total_seconds_year = self.ANNUAL_TRADING_DAYS * self.NSE_SESSION_HOURS * 3600.0
        micro_dt = (step_seconds / max(cfg.micro_steps_per_bar, 1)) / total_seconds_year

        # Pre-calculate drift and diffusion factors
        mu = cfg.drift
        sigma = cfg.volatility

        current_price = float(cfg.start_price)
        bars: list[OHLCVBar] = []

        for sess_open, sess_close in session_intervals:
            session_total_seconds = (sess_close - sess_open).total_seconds()
            curr_bar_time = sess_open

            # Session open small gap (overnight gap model)
            if bars:
                overnight_return = self._rng.gauss(0.0, sigma * math.sqrt(1.0 / self.ANNUAL_TRADING_DAYS) * 0.4)
                current_price *= math.exp(overnight_return)
                current_price = max(current_price, 1.0)

            while curr_bar_time + step <= sess_close:
                bar_open = current_price
                sub_prices = [bar_open]

                # Simulate intra-bar micro-ticks
                for _ in range(cfg.micro_steps_per_bar):
                    z = self._rng.gauss(0.0, 1.0)
                    step_ret = (mu - 0.5 * (sigma ** 2)) * micro_dt + sigma * math.sqrt(micro_dt) * z
                    current_price *= math.exp(step_ret)
                    current_price = max(current_price, 0.5)
                    sub_prices.append(current_price)

                bar_close = current_price
                raw_high = max(sub_prices)
                raw_low = min(sub_prices)

                # Ensure High >= max(Open, Close) and Low <= min(Open, Close) with slight spread
                bar_high = max(raw_high, bar_open, bar_close)
                bar_low = min(raw_low, bar_open, bar_close)

                # Add tiny wick buffer if high == open == close == low
                if bar_high == bar_low:
                    bar_high += 0.05
                    bar_low = max(0.1, bar_low - 0.05)

                # Realistic intraday U-curve volume multiplier
                elapsed = (curr_bar_time - sess_open).total_seconds()
                norm_time = elapsed / max(session_total_seconds, 1.0)  # 0.0 to 1.0
                # Quadratic U-shape: high at 0.0 (open) and 1.0 (close), dipping midday (0.5)
                u_curve = 1.8 - 2.8 * norm_time * (1.0 - norm_time)
                u_curve = max(0.4, u_curve)

                # Log-normal volume noise
                vol_noise = math.exp(self._rng.gauss(0.0, cfg.volume_dispersion))
                base_vol = float(cfg.base_volume) * (step_seconds / 300.0)  # normalized to 5m
                bar_volume = max(10.0, base_vol * u_curve * vol_noise)

                # Decimal conversions rounded to 2 places (INR standard tick 0.05)
                tick_size = cfg.asset.tick_size or Decimal("0.05")
                open_dec = self._round_to_tick(Decimal(str(round(bar_open, 2))), tick_size)
                close_dec = self._round_to_tick(Decimal(str(round(bar_close, 2))), tick_size)
                high_dec = self._round_to_tick(Decimal(str(round(bar_high, 2))), tick_size)
                low_dec = self._round_to_tick(Decimal(str(round(bar_low, 2))), tick_size)

                # Enforce candle invariants strictly after rounding
                high_dec = max(high_dec, open_dec, close_dec)
                low_dec = min(low_dec, open_dec, close_dec)
                vol_dec = Decimal(str(int(bar_volume)))

                bar = OHLCVBar(
                    asset=cfg.asset,
                    timeframe=cfg.timeframe,
                    timestamp=curr_bar_time.astimezone(timezone.utc),
                    open=open_dec,
                    high=high_dec,
                    low=low_dec,
                    close=close_dec,
                    volume=vol_dec,
                    open_interest=None,
                    data_source=DataSource.SYNTHETIC,  # Explicitly flagged as SYNTHETIC
                )
                bars.append(bar)
                curr_bar_time += step

        return bars

    @staticmethod
    def _round_to_tick(val: Decimal, tick_size: Decimal) -> Decimal:
        """Round Decimal value to the nearest exchange tick size increment."""
        steps = (val / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return (steps * tick_size).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
