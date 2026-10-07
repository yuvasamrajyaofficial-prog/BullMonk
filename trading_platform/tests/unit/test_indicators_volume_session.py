"""
Unit tests for volume, session, and flow features:
OBV, VolumeSMA, VolumeRatio, SessionVWAP, CVDProxy, SessionFeatures.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
import numpy as np
import pandas as pd
import pytest

from data.sessions import Crypto247SessionCalendar, NSESessionCalendar
from indicators.session import SessionFeatures
from indicators.volume import (
    OBV,
    CVDProxy,
    SessionVWAP,
    VolumeRatio,
    VolumeSMA,
)


@pytest.fixture
def multi_session_data() -> pd.DataFrame:
    """Fixture providing 2 sessions of 15-minute intraday bars for NSE."""
    # Session 1: 2025-01-02 (09:15 to 10:15 IST = 03:45 to 04:45 UTC)
    # Session 2: 2025-01-03 (09:15 to 10:15 IST = 03:45 to 04:45 UTC)
    ts1 = pd.date_range("2025-01-02 03:45", periods=5, freq="15min", tz="UTC")
    ts2 = pd.date_range("2025-01-03 03:45", periods=5, freq="15min", tz="UTC")
    timestamps = ts1.append(ts2)

    close = [100.0, 102.0, 101.0, 103.0, 105.0, 200.0, 202.0, 201.0, 203.0, 205.0]
    volume = [100.0, 200.0, 150.0, 300.0, 250.0, 500.0, 400.0, 600.0, 300.0, 200.0]

    high = [c + 1.0 for c in close]
    low = [c - 1.0 for c in close]
    open_p = [c - 0.2 for c in close]

    return pd.DataFrame(
        {
            "timestamp": timestamps,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )


class TestOBV:
    def test_obv_calculation(self):
        df = pd.DataFrame(
            {
                "close": [10.0, 12.0, 11.0, 11.0, 14.0],
                "volume": [100.0, 200.0, 150.0, 50.0, 300.0],
            }
        )
        obv = OBV()
        res = obv.calculate(df)

        # Bar 0: 0
        # Bar 1: +200 -> 200
        # Bar 2: -150 -> 50
        # Bar 3: flat -> 50
        # Bar 4: +300 -> 350
        expected = [0.0, 200.0, 50.0, 50.0, 350.0]
        assert np.allclose(res["obv"], expected)


class TestVolumeSMAAndRatio:
    def test_volume_sma_and_ratio(self):
        df = pd.DataFrame({"volume": [100.0, 200.0, 300.0]})
        vsma = VolumeSMA(period=2)
        res_sma = vsma.calculate(df)
        assert math.isclose(res_sma["volume_sma_2"].iloc[1], 150.0)

        vratio = VolumeRatio(period=2)
        res_ratio = vratio.calculate(df)
        # Bar 1 ratio: 200 / 150 = 1.3333
        assert math.isclose(res_ratio["volume_ratio_2"].iloc[1], 200.0 / 150.0, rel_tol=1e-5)


class TestSessionVWAP:
    def test_vwap_resets_per_session(self, multi_session_data: pd.DataFrame):
        cal = NSESessionCalendar()
        vwap_ind = SessionVWAP(calendar=cal, include_deviation=True)
        res = vwap_ind.calculate(multi_session_data)

        assert "vwap" in res.columns
        assert "vwap_deviation" in res.columns

        # Check session 1 bar 0
        tp0 = (multi_session_data["high"].iloc[0] + multi_session_data["low"].iloc[0] + multi_session_data["close"].iloc[0]) / 3.0
        assert math.isclose(res["vwap"].iloc[0], tp0, rel_tol=1e-5)

        # Check session 2 bar 5 (first bar of day 2)
        tp5 = (multi_session_data["high"].iloc[5] + multi_session_data["low"].iloc[5] + multi_session_data["close"].iloc[5]) / 3.0
        # VWAP must reset to tp5 and NOT carry over the session 1 volume/PV
        assert math.isclose(res["vwap"].iloc[5], tp5, rel_tol=1e-5)

    def test_vwap_crypto_continuous(self):
        # Continuous 24/7 crypto dates
        cal = Crypto247SessionCalendar()
        ts = pd.date_range("2025-01-01 23:00", periods=3, freq="1h", tz="UTC")
        df = pd.DataFrame({
            "timestamp": ts,
            "open": [100.0, 105.0, 110.0],
            "high": [101.0, 106.0, 111.0],
            "low": [99.0, 104.0, 109.0],
            "close": [100.0, 105.0, 110.0],
            "volume": [10.0, 20.0, 30.0],
        })
        vwap_ind = SessionVWAP(calendar=cal)
        res = vwap_ind.calculate(df)
        assert len(res) == 3


class TestCVDProxy:
    def test_cvd_proxy_calculations(self):
        # Case 1: Close == High (Bullish extreme: delta = +Volume)
        # Case 2: Close == Low (Bearish extreme: delta = -Volume)
        # Case 3: Flat candle High == Low (Zero range: delta = 0.0)
        df = pd.DataFrame(
            {
                "high": [110.0, 110.0, 100.0],
                "low": [100.0, 100.0, 100.0],  # Bar 2 is flat candle (100 == 100)
                "close": [110.0, 100.0, 100.0],
                "volume": [100.0, 200.0, 300.0],
            }
        )
        cvd = CVDProxy()
        res = cvd.calculate(df)

        assert "candle_delta" in res.columns
        assert "cumulative_delta" in res.columns

        deltas = res["candle_delta"].values
        # Bar 0: +100
        assert math.isclose(deltas[0], 100.0, rel_tol=1e-5)
        # Bar 1: -200
        assert math.isclose(deltas[1], -200.0, rel_tol=1e-5)
        # Bar 2: High == Low -> zero without division-by-zero crash
        assert math.isclose(deltas[2], 0.0, abs_tol=1e-5)

        # Cumulative delta
        assert math.isclose(res["cumulative_delta"].iloc[2], -100.0, rel_tol=1e-5)


class TestSessionFeatures:
    def test_session_features_and_opening_range(self, multi_session_data: pd.DataFrame):
        sess = SessionFeatures(calendar=NSESessionCalendar(), opening_range_bars=2)
        res = sess.calculate(multi_session_data)

        assert "session_open" in res.columns
        assert "session_high" in res.columns
        assert "session_low" in res.columns
        assert "opening_range_high_2" in res.columns
        assert "opening_range_low_2" in res.columns

        # Verify session open in day 1 equals open of bar 0
        assert res["session_open"].iloc[0] == multi_session_data["open"].iloc[0]
        assert res["session_open"].iloc[4] == multi_session_data["open"].iloc[0]

        # Verify session open in day 2 resets to bar 5
        assert res["session_open"].iloc[5] == multi_session_data["open"].iloc[5]
