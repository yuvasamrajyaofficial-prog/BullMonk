"""
Unit tests for volatility indicators: ATR, BollingerBands, BollingerBandWidth, HistoricalVolatility.
"""

from __future__ import annotations

import math
import numpy as np
import pandas as pd
import pytest

from indicators.volatility import ATR, BollingerBands, BollingerBandWidth, HistoricalVolatility


@pytest.fixture
def sample_data() -> pd.DataFrame:
    n = 50
    dates = pd.date_range("2025-01-01", periods=n, freq="1D", tz="UTC")
    close = 100.0 + np.cumsum(np.random.RandomState(42).randn(n) * 2.0)
    high = close + 1.5
    low = close - 1.5
    open_p = close - 0.2
    return pd.DataFrame(
        {"timestamp": dates, "open": open_p, "high": high, "low": low, "close": close}
    )


class TestATR:
    def test_atr_basic(self, sample_data: pd.DataFrame):
        atr = ATR(period=14)
        res = atr.calculate(sample_data)

        assert "atr_14" in res.columns
        valid_atr = res["atr_14"].dropna()
        assert len(valid_atr) > 0
        assert (valid_atr > 0).all()

    def test_atr_true_range_gap(self):
        # Explicit gap: Bar 1: H=10, L=8, C=9. Bar 2: H=20, L=18, C=19.
        # Bar 2 TR = max(20-18, |20-9|, |18-9|) = max(2, 11, 9) = 11.0
        df = pd.DataFrame(
            {
                "high": [10.0, 20.0],
                "low": [8.0, 18.0],
                "close": [9.0, 19.0],
            }
        )
        atr = ATR(period=1)
        res = atr.calculate(df)
        assert math.isclose(res["atr_1"].iloc[1], 11.0, rel_tol=1e-5)


class TestBollingerBands:
    def test_bollinger_bands(self, sample_data: pd.DataFrame):
        bb = BollingerBands(period=20, std_dev=2.0)
        res = bb.calculate(sample_data)

        upper_col = "bb_upper_20_2.0"
        mid_col = "bb_middle_20"
        lower_col = "bb_lower_20_2.0"
        width_col = "bb_width_20_2.0"
        pct_b_col = "bb_percent_b_20_2.0"

        for col in (upper_col, mid_col, lower_col, width_col, pct_b_col):
            assert col in res.columns

        valid = res.dropna()
        # Upper >= Middle >= Lower
        assert (valid[upper_col] >= valid[mid_col]).all()
        assert (valid[mid_col] >= valid[lower_col]).all()

        # Width = (Upper - Lower) / Middle
        expected_width = (valid[upper_col] - valid[lower_col]) / valid[mid_col]
        assert np.allclose(valid[width_col], expected_width, atol=1e-5)


class TestBollingerBandWidth:
    def test_bandwidth(self, sample_data: pd.DataFrame):
        bbw = BollingerBandWidth(period=20, std_dev=2.0)
        res = bbw.calculate(sample_data)
        assert "bb_width_20_2.0" in res.columns
        assert (res["bb_width_20_2.0"].dropna() >= 0).all()


class TestHistoricalVolatility:
    def test_historical_volatility(self, sample_data: pd.DataFrame):
        hv = HistoricalVolatility(period=20, trading_days=252)
        res = hv.calculate(sample_data)

        assert "hist_vol_20" in res.columns
        valid_hv = res["hist_vol_20"].dropna()
        assert len(valid_hv) > 0
        assert (valid_hv >= 0).all()
