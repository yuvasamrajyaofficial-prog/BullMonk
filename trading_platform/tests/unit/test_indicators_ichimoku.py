"""
Unit tests for IchimokuCloud:
Calculations, causality verification, look-ahead protection, and derived features.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from indicators.ichimoku import IchimokuCloud


@pytest.fixture
def ichimoku_test_df() -> pd.DataFrame:
    n = 120
    dates = pd.date_range("2025-01-01", periods=n, freq="1D", tz="UTC")
    # Upward trending series
    close = np.linspace(100.0, 220.0, n)
    high = close + 5.0
    low = close - 5.0
    open_p = close - 1.0

    return pd.DataFrame(
        {"timestamp": dates, "open": open_p, "high": high, "low": low, "close": close}
    )


class TestIchimokuCloud:
    def test_tenkan_and_kijun(self, ichimoku_test_df: pd.DataFrame):
        ich = IchimokuCloud(conversion_period=9, base_period=26, leading_span_b_period=52, displacement=26)
        res = ich.calculate(ichimoku_test_df)

        assert "tenkan" in res.columns
        assert "kijun" in res.columns
        assert "senkou_a" in res.columns
        assert "senkou_b" in res.columns
        assert "chikou" in res.columns

        # Tenkan first 8 values are NaN, 9th is (max(H[:9]) + min(L[:9])) / 2
        assert res["tenkan"].iloc[:8].isna().all()
        assert not np.isnan(res["tenkan"].iloc[8])

        # Kijun first 25 values are NaN, 26th is valid
        assert res["kijun"].iloc[:25].isna().all()
        assert not np.isnan(res["kijun"].iloc[25])

    def test_senkou_causal_alignment_warmup(self, ichimoku_test_df: pd.DataFrame):
        """
        Verify that Senkou A and B are shifted by displacement (26 bars).
        Because Senkou A requires 26 bars (Kijun) + 26 displacement = 52 bars warmup.
        Senkou B requires 52 bars + 26 displacement = 78 bars warmup.
        """
        ich = IchimokuCloud(conversion_period=9, base_period=26, leading_span_b_period=52, displacement=26)
        res = ich.calculate(ichimoku_test_df)

        # Senkou B must be NaN for the first 77 bars
        assert res["senkou_b"].iloc[:77].isna().all()
        assert not np.isnan(res["senkou_b"].iloc[77])

    def test_derived_features(self, ichimoku_test_df: pd.DataFrame):
        ich = IchimokuCloud(conversion_period=9, base_period=26, leading_span_b_period=52, displacement=26)
        res = ich.calculate(ichimoku_test_df)

        # In a sustained strong bull market with close rising steadily:
        # Price should be above cloud, Tenkan > Kijun, Cloud bullish (Senkou A > Senkou B)
        last_row = res.iloc[-1]
        assert last_row["price_above_cloud"] == 1.0
        assert last_row["price_below_cloud"] == 0.0
        assert last_row["price_inside_cloud"] == 0.0
        assert last_row["tenkan_above_kijun"] == 1.0
        assert last_row["cloud_bullish"] == 1.0
        assert last_row["cloud_width"] > 0

    def test_zero_look_ahead_bias(self, ichimoku_test_df: pd.DataFrame):
        """
        CRITICAL TEST:
        Changing candle data at time T+1 (or T+26) must NOT alter
        any indicator output at time <= T.
        """
        ich = IchimokuCloud(conversion_period=9, base_period=26, leading_span_b_period=52, displacement=26)
        df_base = ichimoku_test_df.copy()
        res_base = ich.calculate(df_base)

        # Create modified dataset where bar 100 has a massive price spike
        df_modified = ichimoku_test_df.copy()
        df_modified.loc[100, "high"] = 9999.0
        df_modified.loc[100, "close"] = 9998.0
        res_modified = ich.calculate(df_modified)

        # Values at index 0..99 must be 100% BITWISE IDENTICAL
        cols_to_check = ["tenkan", "kijun", "senkou_a", "senkou_b", "price_above_cloud"]
        for col in cols_to_check:
            base_slice = res_base.loc[:99, col]
            mod_slice = res_modified.loc[:99, col]
            pd.testing.assert_series_equal(base_slice, mod_slice)
