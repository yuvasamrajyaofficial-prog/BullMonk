"""
Unit tests for trend indicators: SMA, EMA, WMA, HMA, ADX, Supertrend.
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
import pytest

from indicators.trend import ADX, EMA, HMA, SMA, WMA, Supertrend
from indicators.validation import IndicatorValidationError


@pytest.fixture
def sample_ohlcv() -> pd.DataFrame:
    """Fixture providing simple deterministic OHLCV data."""
    dates = pd.date_range("2025-01-01", periods=60, freq="1D", tz="UTC")
    # Monotonically increasing close prices
    close = np.linspace(100.0, 160.0, 60)
    high = close + 2.0
    low = close - 2.0
    open_p = close - 0.5
    volume = np.full(60, 1000.0)

    return pd.DataFrame(
        {
            "timestamp": dates,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


class TestSMA:
    def test_sma_calculation(self, sample_ohlcv: pd.DataFrame):
        sma = SMA(period=5)
        res = sma.calculate(sample_ohlcv)

        assert "sma_5" in res.columns
        # First 4 values should be NaN
        assert res["sma_5"].iloc[:4].isna().all()
        # 5th value: mean of [100.0, 101.0169..., ...]
        expected_5th = sample_ohlcv["close"].iloc[:5].mean()
        assert math.isclose(res["sma_5"].iloc[4], expected_5th, rel_tol=1e-5)

    def test_invalid_period(self):
        with pytest.raises(ValueError, match="positive integer"):
            SMA(period=0)


class TestEMA:
    def test_ema_warmup_and_calculation(self, sample_ohlcv: pd.DataFrame):
        ema = EMA(period=10)
        res = ema.calculate(sample_ohlcv)

        assert "ema_10" in res.columns
        # First 9 values must be NaN due to warmup requirement
        assert res["ema_10"].iloc[:9].isna().all()
        assert not np.isnan(res["ema_10"].iloc[9])

    def test_invalid_period(self):
        with pytest.raises(ValueError):
            EMA(period=-5)


class TestWMA:
    def test_wma_calculation(self):
        # Known small vector: [10, 20, 30] with weights [1, 2, 3] -> (10*1 + 20*2 + 30*3)/(1+2+3) = 140/6 = 23.3333
        df = pd.DataFrame({"close": [10.0, 20.0, 30.0]})
        wma = WMA(period=3)
        res = wma.calculate(df)

        assert res["wma_3"].iloc[0:2].isna().all()
        expected = (10.0 * 1 + 20.0 * 2 + 30.0 * 3) / 6.0
        assert math.isclose(res["wma_3"].iloc[2], expected, rel_tol=1e-5)


class TestHMA:
    def test_hma_warmup_and_calculation(self, sample_ohlcv: pd.DataFrame):
        hma = HMA(period=16)
        res = hma.calculate(sample_ohlcv)

        assert "hma_16" in res.columns
        warmup = hma.warmup_period
        assert res["hma_16"].iloc[warmup + 5] > 0


class TestADX:
    def test_adx_outputs(self, sample_ohlcv: pd.DataFrame):
        adx = ADX(period=14)
        res = adx.calculate(sample_ohlcv)

        assert "adx_14" in res.columns
        assert "plus_di_14" in res.columns
        assert "minus_di_14" in res.columns

        # For a pure uptrend, +DI must be significantly greater than -DI
        valid_idx = res["adx_14"].dropna().index[-1]
        assert res.loc[valid_idx, "plus_di_14"] > res.loc[valid_idx, "minus_di_14"]
        assert res.loc[valid_idx, "adx_14"] > 0


class TestSupertrend:
    def test_supertrend_bullish_uptrend(self, sample_ohlcv: pd.DataFrame):
        st = Supertrend(period=7, multiplier=2.0)
        res = st.calculate(sample_ohlcv)

        col_st = "supertrend_7_2.0"
        col_dir = "supertrend_direction_7_2.0"
        assert col_st in res.columns
        assert col_dir in res.columns

        # In a sustained strong uptrend, direction should be +1 (bullish)
        assert res[col_dir].iloc[-1] == 1.0
        assert res[col_st].iloc[-1] <= sample_ohlcv["close"].iloc[-1]

    def test_supertrend_bearish_downtrend(self):
        # Monotonically dropping market
        close = np.linspace(200.0, 100.0, 30)
        df = pd.DataFrame({
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
        })
        st = Supertrend(period=5, multiplier=2.0)
        res = st.calculate(df)

        col_dir = "supertrend_direction_5_2.0"
        col_st = "supertrend_7_2.0"
        # At end of drop, direction must be -1 (bearish)
        assert res[col_dir].iloc[-1] == -1.0
