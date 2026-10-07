"""
Unit tests for FeaturePipeline, IndicatorRegistry, data validation,
look-ahead protection, determinism, and performance.
"""

from __future__ import annotations

import time
import numpy as np
import pandas as pd
import pytest

from core.enums import Timeframe
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
from indicators import (
    ATR,
    EMA,
    RSI,
    FeaturePipeline,
    IchimokuCloud,
    IndicatorRegistry,
    IndicatorValidationError,
    SessionVWAP,
    default_registry,
    validate_dataframe,
)


@pytest.fixture
def clean_synthetic_data() -> pd.DataFrame:
    """Generate deterministic synthetic data using Phase 2 generator."""
    gen = SyntheticOHLCVGenerator(seed=42)
    cfg = SyntheticDataConfig(
        number_of_sessions=3,
        timeframe=Timeframe.M5,
        seed=42,
    )
    bars = gen.generate(cfg)
    return pd.DataFrame(
        [
            {
                "timestamp": b.timestamp,
                "open": float(b.open),
                "high": float(b.high),
                "low": float(b.low),
                "close": float(b.close),
                "volume": float(b.volume),
            }
            for b in bars
        ]
    )


class TestDataValidation:
    def test_reject_empty_dataframe(self):
        with pytest.raises(IndicatorValidationError, match="empty"):
            validate_dataframe(pd.DataFrame())

    def test_reject_missing_columns(self):
        df = pd.DataFrame({"open": [10.0], "close": [11.0]})
        with pytest.raises(IndicatorValidationError, match="Missing required columns"):
            validate_dataframe(df, required_columns=("high", "low", "close"))

    def test_reject_unsorted_timestamps(self):
        ts = pd.to_datetime(["2025-01-02", "2025-01-01"])
        df = pd.DataFrame({"timestamp": ts, "close": [10.0, 11.0]})
        with pytest.raises(IndicatorValidationError, match="unsorted"):
            validate_dataframe(df, required_columns=("close",))

    def test_reject_duplicate_timestamps(self):
        ts = pd.to_datetime(["2025-01-01 10:00", "2025-01-01 10:00"])
        df = pd.DataFrame({"timestamp": ts, "close": [10.0, 11.0]})
        with pytest.raises(IndicatorValidationError, match="Duplicate timestamp"):
            validate_dataframe(df, required_columns=("close",))

    def test_reject_invalid_ohlc(self):
        # High < Low
        df_bad_hl = pd.DataFrame({
            "open": [10.0],
            "high": [8.0],
            "low": [9.0],
            "close": [8.5],
        })
        with pytest.raises(IndicatorValidationError, match="High is strictly less than Low"):
            validate_dataframe(df_bad_hl, required_columns=("high", "low", "close"))

        # Low > Open
        df_bad_lo = pd.DataFrame({
            "open": [10.0],
            "high": [12.0],
            "low": [11.0],
            "close": [11.5],
        })
        with pytest.raises(IndicatorValidationError, match="Low is strictly greater than Open"):
            validate_dataframe(df_bad_lo, required_columns=("open", "high", "low", "close"))

    def test_reject_negative_volume(self):
        df_bad_vol = pd.DataFrame({"close": [10.0], "volume": [-50.0]})
        with pytest.raises(IndicatorValidationError, match="Negative volume"):
            validate_dataframe(df_bad_vol, required_columns=("close", "volume"))


class TestFeaturePipeline:
    def test_pipeline_assembly(self, clean_synthetic_data: pd.DataFrame):
        pipeline = FeaturePipeline([
            EMA(period=10),
            EMA(period=20),
            RSI(period=14),
            ATR(period=14),
            SessionVWAP(),
            IchimokuCloud(),
        ])

        assert pipeline.max_warmup_period == 52 + 26  # Ichimoku warmup
        features = pipeline.calculate(clean_synthetic_data)

        # Ensure all columns present
        expected_cols = [
            "ema_10",
            "ema_20",
            "rsi_14",
            "atr_14",
            "vwap",
            "tenkan",
            "kijun",
            "senkou_a",
            "senkou_b",
        ]
        for col in expected_cols:
            assert col in features.columns

        # Index and timestamp integrity preserved
        assert len(features) == len(clean_synthetic_data)
        assert (features["timestamp"] == clean_synthetic_data["timestamp"]).all()

        # Warm data filtering
        warm_df = pipeline.get_warm_data(clean_synthetic_data)
        assert len(warm_df) > 0
        assert len(warm_df) < len(clean_synthetic_data)
        assert pipeline.is_warm(warm_df).all()

    def test_pipeline_collision_detection(self):
        # Adding duplicate indicator with same parameters should raise collision error
        with pytest.raises(ValueError, match="collision"):
            pipeline = FeaturePipeline([EMA(period=20), EMA(period=20)])
            df = pd.DataFrame({"close": np.linspace(10, 50, 30)})
            pipeline.calculate(df)

    def test_look_ahead_protection(self, clean_synthetic_data: pd.DataFrame):
        """
        Verify that adding future bars does NOT change any previously calculated features.
        """
        pipeline = FeaturePipeline([
            EMA(period=15),
            RSI(period=14),
            ATR(period=14),
            IchimokuCloud(),
        ])

        # Slice to first 150 bars
        df_t = clean_synthetic_data.iloc[:150].copy()
        features_t = pipeline.calculate(df_t)

        # Full dataset (more bars into future)
        features_full = pipeline.calculate(clean_synthetic_data)

        # Compare features for the first 150 bars
        for col in ["ema_15", "rsi_14", "atr_14", "tenkan", "kijun", "senkou_a", "senkou_b"]:
            t_vals = features_t[col]
            full_vals = features_full.iloc[:150][col]
            pd.testing.assert_series_equal(t_vals, full_vals, check_names=False)

    def test_deterministic_output(self, clean_synthetic_data: pd.DataFrame):
        pipeline = FeaturePipeline([EMA(period=20), RSI(period=14)])
        res1 = pipeline.calculate(clean_synthetic_data)
        res2 = pipeline.calculate(clean_synthetic_data)

        pd.testing.assert_frame_equal(res1, res2)


class TestIndicatorRegistry:
    def test_registry_lookup_and_get(self):
        reg = default_registry

        # Case-insensitive lookup
        rsi = reg.get("rsi", period=14)
        assert rsi.name == "RSI"
        assert rsi.warmup_period == 15

        ema = reg.get("EMA", period=50)
        assert ema.name == "EMA"

        # List indicators returns dictionary of metadata
        ind_list = reg.list_indicators()
        assert "RSI" in ind_list
        assert "EMA" in ind_list
        assert "ICHIMOKU" in ind_list
        assert "VWAP" in ind_list
        assert "ATR" in ind_list

    def test_registry_unknown_indicator(self):
        reg = default_registry
        with pytest.raises(KeyError, match="not found in registry"):
            reg.get("NON_EXISTENT_INDICATOR")


class TestPerformanceOnLargeDataset:
    def test_large_dataset_performance(self):
        """
        Performance verification: 50,000 bars should calculate within a few seconds.
        """
        n = 50_000
        dates = pd.date_range("2020-01-01", periods=n, freq="1min", tz="UTC")
        close = 100.0 + np.cumsum(np.random.RandomState(42).randn(n) * 0.1)
        high = close + 0.5
        low = close - 0.5
        open_p = close - 0.1
        volume = np.full(n, 100.0)

        df = pd.DataFrame({
            "timestamp": dates,
            "open": open_p,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        })

        pipeline = FeaturePipeline([
            EMA(period=20),
            EMA(period=50),
            RSI(period=14),
            ATR(period=14),
        ])

        start_time = time.perf_counter()
        features = pipeline.calculate(df)
        elapsed = time.perf_counter() - start_time

        assert len(features) == n
        # Must execute within 5 seconds for 50k rows
        assert elapsed < 5.0, f"Pipeline took {elapsed:.2f}s, expected < 5s"
