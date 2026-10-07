"""
Unit tests for the SyntheticOHLCVGenerator.

Tests:
1. Realistic OHLC relationships (High >= max(O,C), Low <= min(O,C), Low <= High).
2. Non-negative volume (Volume >= 0).
3. Deterministic repeatability with seed.
4. Different seeds produce distinct trajectories.
5. All generated bars explicitly marked as DataSource.SYNTHETIC.
6. Correct number of bars per session for given timeframe.
7. Timestamps strictly within session hours and in chronological order.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from core.enums import DataSource, Timeframe
from data.nifty import create_nifty_index
from data.sessions import NSESessionCalendar
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator


class TestSyntheticGenerator:

    def test_deterministic_reproducibility(self):
        """Same seed must produce 100% identical bars."""
        gen1 = SyntheticOHLCVGenerator(seed=123)
        gen2 = SyntheticOHLCVGenerator(seed=123)

        cfg = SyntheticDataConfig(number_of_sessions=2, seed=123)
        bars1 = gen1.generate(cfg)
        bars2 = gen2.generate(cfg)

        assert len(bars1) == len(bars2)
        for b1, b2 in zip(bars1, bars2):
            assert b1.timestamp == b2.timestamp
            assert b1.open == b2.open
            assert b1.high == b2.high
            assert b1.low == b2.low
            assert b1.close == b2.close
            assert b1.volume == b2.volume

    def test_different_seeds_produce_different_paths(self):
        """Different seeds must yield different price paths."""
        gen = SyntheticOHLCVGenerator()
        cfg1 = SyntheticDataConfig(number_of_sessions=2, seed=100)
        cfg2 = SyntheticDataConfig(number_of_sessions=2, seed=200)

        bars1 = gen.generate(cfg1)
        bars2 = gen.generate(cfg2)

        # Final close should differ
        assert bars1[-1].close != bars2[-1].close

    def test_ohlc_invariants_strictly_enforced(self):
        """All bars must satisfy High >= max(Open, Close) and Low <= min(Open, Close)."""
        gen = SyntheticOHLCVGenerator(seed=42)
        cfg = SyntheticDataConfig(number_of_sessions=3, timeframe=Timeframe.M5, seed=42)
        bars = gen.generate(cfg)

        assert len(bars) > 0
        for b in bars:
            assert b.high >= b.open, f"High ({b.high}) < Open ({b.open})"
            assert b.high >= b.close, f"High ({b.high}) < Close ({b.close})"
            assert b.low <= b.open, f"Low ({b.low}) > Open ({b.open})"
            assert b.low <= b.close, f"Low ({b.low}) > Close ({b.close})"
            assert b.low <= b.high, f"Low ({b.low}) > High ({b.high})"
            assert b.volume >= 0, f"Negative volume: {b.volume}"

    def test_provenance_is_always_synthetic(self):
        """Synthetic bars must be tagged with DataSource.SYNTHETIC and is_synthetic=True."""
        gen = SyntheticOHLCVGenerator(seed=99)
        bars = gen.generate(SyntheticDataConfig(number_of_sessions=1, seed=99))

        for b in bars:
            assert b.data_source == DataSource.SYNTHETIC
            assert b.is_synthetic is True

    def test_correct_bar_count_for_nse_session(self):
        """
        NSE session: 09:15 to 15:30 = 375 minutes.
        For 5m bars: 375 / 5 = 75 bars per session.
        For 3 sessions: 3 * 75 = 225 bars.
        """
        gen = SyntheticOHLCVGenerator(seed=42)
        cfg = SyntheticDataConfig(
            number_of_sessions=3,
            timeframe=Timeframe.M5,
            start_date=date(2025, 1, 6),
            seed=42,
        )
        bars = gen.generate(cfg)
        assert len(bars) == 225

    def test_strictly_chronological_and_within_session(self):
        """Timestamps must strictly increase and fall inside trading hours."""
        cal = NSESessionCalendar()
        gen = SyntheticOHLCVGenerator(seed=42)
        bars = gen.generate(SyntheticDataConfig(number_of_sessions=2, seed=42))

        for i in range(1, len(bars)):
            assert bars[i].timestamp > bars[i - 1].timestamp

        for b in bars:
            assert cal.is_market_open(b.timestamp)

    def test_invalid_config_raises(self):
        """Invalid config values should fail gracefully."""
        with pytest.raises(ValueError):
            SyntheticDataConfig(start_price=Decimal("-10"))
        with pytest.raises(ValueError):
            SyntheticDataConfig(volatility=-0.05)
        with pytest.raises(ValueError):
            SyntheticDataConfig(number_of_sessions=0)
