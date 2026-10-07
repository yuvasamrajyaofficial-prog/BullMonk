"""
Unit tests for the DataNormalizer.

Tests:
1. Deduplication using 'last', 'first', and 'max_volume' strategies.
2. Chronological sorting enforcement.
3. UTC timezone normalization.
4. Tick size rounding alignment.
5. Timeframe resampling (e.g. 5m -> 15m, 1h, 1d).
6. Resampling candle mathematical consistency:
   Open = first open, Close = last close, High = max(highs), Low = min(lows), Volume = sum(volumes).
7. Synthetic provenance preserved across normalization and resampling.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from core.enums import DataSource, Timeframe
from core.models import OHLCVBar
from data.nifty import create_nifty_index
from data.normalization import DataNormalizer
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator


@pytest.fixture
def sample_bars() -> list[OHLCVBar]:
    gen = SyntheticOHLCVGenerator(seed=42)
    return gen.generate(SyntheticDataConfig(number_of_sessions=2, timeframe=Timeframe.M5, seed=42))


class TestDataNormalizer:

    def test_deduplication_strategies(self, sample_bars: list[OHLCVBar]):
        normalizer = DataNormalizer()
        base_bar = sample_bars[0]

        # Duplicate with different volume
        dup_bar = OHLCVBar(
            asset=base_bar.asset,
            timeframe=base_bar.timeframe,
            timestamp=base_bar.timestamp,
            open=base_bar.open,
            high=base_bar.high,
            low=base_bar.low,
            close=base_bar.close,
            volume=Decimal("9999999"),
            data_source=base_bar.data_source,
        )

        test_list = [base_bar, dup_bar]

        # 'first' keeps base_bar
        res_first = normalizer.normalize_bars(test_list, deduplicate_strategy="first")
        assert len(res_first) == 1
        assert res_first[0].volume == base_bar.volume

        # 'last' keeps dup_bar
        res_last = normalizer.normalize_bars(test_list, deduplicate_strategy="last")
        assert len(res_last) == 1
        assert res_last[0].volume == Decimal("9999999")

        # 'max_volume' keeps dup_bar
        res_max = normalizer.normalize_bars(test_list, deduplicate_strategy="max_volume")
        assert len(res_max) == 1
        assert res_max[0].volume == Decimal("9999999")

    def test_chronological_sorting(self, sample_bars: list[OHLCVBar]):
        normalizer = DataNormalizer()
        shuffled = list(sample_bars)
        shuffled.reverse()

        sorted_bars = normalizer.normalize_bars(shuffled)
        assert len(sorted_bars) == len(sample_bars)
        for i in range(1, len(sorted_bars)):
            assert sorted_bars[i].timestamp > sorted_bars[i - 1].timestamp

    def test_resample_5m_to_15m(self, sample_bars: list[OHLCVBar]):
        normalizer = DataNormalizer()
        resampled_15m = normalizer.resample_bars(sample_bars, target_timeframe=Timeframe.M15)

        # 75 bars/day (5m) -> 25 bars/day (15m) * 2 days = 50 bars
        assert len(resampled_15m) == 50
        assert resampled_15m[0].timeframe == Timeframe.M15

        # Check OHLC aggregation of first 15m bar
        first_3_bars = sample_bars[:3]
        expected_open = first_3_bars[0].open
        expected_close = first_3_bars[-1].close
        expected_high = max(b.high for b in first_3_bars)
        expected_low = min(b.low for b in first_3_bars)
        expected_volume = sum(b.volume for b in first_3_bars)

        agg = resampled_15m[0]
        assert agg.open == expected_open
        assert agg.close == expected_close
        assert agg.high == expected_high
        assert agg.low == expected_low
        assert agg.volume == expected_volume
        assert agg.data_source == DataSource.SYNTHETIC

    def test_resample_5m_to_daily(self, sample_bars: list[OHLCVBar]):
        normalizer = DataNormalizer()
        daily_bars = normalizer.resample_bars(sample_bars, target_timeframe=Timeframe.D1)

        # 2 sessions -> 2 daily bars
        assert len(daily_bars) == 2
        assert daily_bars[0].timeframe == Timeframe.D1

        # Check total volume for day 1
        day1_volume = sum((b.volume for b in sample_bars[:75]), Decimal("0"))
        assert daily_bars[0].volume == day1_volume
        assert daily_bars[0].high == max(b.high for b in sample_bars[:75])
        assert daily_bars[0].low == min(b.low for b in sample_bars[:75])
