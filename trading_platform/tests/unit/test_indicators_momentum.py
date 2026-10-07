"""
Unit tests for momentum indicators: RSI, StochasticOscillator, StochasticRSI, MACD, ROC.
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
import pytest

from indicators.momentum import MACD, ROC, RSI, StochasticOscillator, StochasticRSI


@pytest.fixture
def oscillating_ohlcv() -> pd.DataFrame:
    """Fixture providing cyclical oscillating OHLCV data."""
    n = 100
    dates = pd.date_range("2025-01-01", periods=n, freq="1h", tz="UTC")
    t = np.linspace(0, 4 * np.pi, n)
    base = 100.0 + 10.0 * np.sin(t)
    high = base + 1.5
    low = base - 1.5
    open_p = base - 0.2
    close = base + 0.3
    volume = np.full(n, 500.0)

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


class TestRSI:
    def test_rsi_bounds_and_warmup(self, oscillating_ohlcv: pd.DataFrame):
        rsi = RSI(period=14)
        res = rsi.calculate(oscillating_ohlcv)

        col = "rsi_14"
        assert col in res.columns
        # First 14 values must be NaN
        assert res[col].iloc[:14].isna().all()

        valid_vals = res[col].dropna()
        # RSI must strictly lie between 0 and 100
        assert (valid_vals >= 0.0).all()
        assert (valid_vals <= 100.0).all()

    def test_rsi_constant_price(self):
        # When price does not change, avg gain and loss are 0 -> RSI = 50.0
        df = pd.DataFrame({"close": [100.0] * 30})
        rsi = RSI(period=10)
        res = rsi.calculate(df)
        assert res["rsi_10"].iloc[-1] == 50.0


class TestStochasticOscillator:
    def test_stochastic_oscillator(self, oscillating_ohlcv: pd.DataFrame):
        stoch = StochasticOscillator(k_period=14, d_period=3, slowing=3)
        res = stoch.calculate(oscillating_ohlcv)

        assert "stoch_k_14" in res.columns
        assert "stoch_d_3" in res.columns

        valid_k = res["stoch_k_14"].dropna()
        valid_d = res["stoch_d_3"].dropna()
        assert (valid_k >= 0.0).all() and (valid_k <= 100.0).all()
        assert (valid_d >= 0.0).all() and (valid_d <= 100.0).all()


class TestStochasticRSI:
    def test_stochastic_rsi(self, oscillating_ohlcv: pd.DataFrame):
        stoch_rsi = StochasticRSI(rsi_period=14, stoch_period=14, k_period=3, d_period=3)
        res = stoch_rsi.calculate(oscillating_ohlcv)

        assert "stoch_rsi_k_14" in res.columns
        assert "stoch_rsi_d_3" in res.columns

        valid_k = res["stoch_rsi_k_14"].dropna()
        assert (valid_k >= 0.0).all() and (valid_k <= 100.0).all()


class TestMACD:
    def test_macd_calculation(self, oscillating_ohlcv: pd.DataFrame):
        macd = MACD(fast_period=12, slow_period=26, signal_period=9)
        res = macd.calculate(oscillating_ohlcv)

        m_col = "macd_12_26"
        s_col = "macd_signal_9"
        h_col = "macd_hist_12_26_9"

        assert m_col in res.columns
        assert s_col in res.columns
        assert h_col in res.columns

        # Verify histogram = macd - signal
        valid = res.dropna()
        diff = (valid[m_col] - valid[s_col]) - valid[h_col]
        assert np.allclose(diff, 0.0, atol=1e-10)


class TestROC:
    def test_roc_calculation(self):
        # 100 -> 110 is +10%
        df = pd.DataFrame({"close": [100.0, 105.0, 110.0]})
        roc = ROC(period=2)
        res = roc.calculate(df)

        assert res["roc_2"].iloc[:2].isna().all()
        assert math.isclose(res["roc_2"].iloc[2], 10.0, rel_tol=1e-5)
