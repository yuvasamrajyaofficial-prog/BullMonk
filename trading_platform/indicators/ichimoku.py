"""
Ichimoku Kinko Hyo indicator for the BullMonk quantitative engine.

Strictly preserves causality and prevents look-ahead bias:
- In charting packages, Senkou Span A and B are conventionally drawn 26 bars ahead.
- In this quantitative engine, the active cloud levels at timestamp T represent the
  projections made at (T - displacement) that arrive at timestamp T.
  Thus, price at timestamp T is evaluated against the cloud that was projected into T.
- Chikou Span at timestamp T evaluates Close(T) against Close(T - displacement).
- No future candle data is ever accessed at timestamp T.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


class IchimokuCloud(Indicator):
    """
    Ichimoku Kinko Hyo (Equilibrium Chart).

    Default parameters:
    - conversion_period (Tenkan): 9
    - base_period (Kijun): 26
    - leading_span_b_period (Senkou B): 52
    - displacement: 26

    Outputs:
    - tenkan: (9-period high + 9-period low) / 2
    - kijun: (26-period high + 26-period low) / 2
    - senkou_a: Active leading span A at timestamp T (shifted by +displacement)
    - senkou_b: Active leading span B at timestamp T (shifted by +displacement)
    - chikou: Close price from (T - displacement) for comparison
    - price_above_cloud: Boolean (Close > max(senkou_a, senkou_b))
    - price_below_cloud: Boolean (Close < min(senkou_a, senkou_b))
    - price_inside_cloud: Boolean (min <= Close <= max)
    - tenkan_above_kijun: Boolean (tenkan > kijun)
    - tenkan_below_kijun: Boolean (tenkan < kijun)
    - cloud_bullish: Boolean (senkou_a > senkou_b)
    - cloud_bearish: Boolean (senkou_a < senkou_b)
    - cloud_width: abs(senkou_a - senkou_b)
    """

    def __init__(
        self,
        conversion_period: int = 9,
        base_period: int = 26,
        leading_span_b_period: int = 52,
        displacement: int = 26,
    ) -> None:
        if conversion_period <= 0 or base_period <= 0 or leading_span_b_period <= 0:
            raise ValueError("All period parameters must be positive integers")
        if displacement < 0:
            raise ValueError("displacement must be >= 0")

        self.conversion_period = conversion_period
        self.base_period = base_period
        self.leading_span_b_period = leading_span_b_period
        self.displacement = displacement

        self._output_columns = (
            "tenkan",
            "kijun",
            "senkou_a",
            "senkou_b",
            "chikou",
            "price_above_cloud",
            "price_below_cloud",
            "price_inside_cloud",
            "tenkan_above_kijun",
            "tenkan_below_kijun",
            "cloud_bullish",
            "cloud_bearish",
            "cloud_width",
        )

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="IchimokuCloud",
            version="1.0.0",
            description="Ichimoku Kinko Hyo with causal cloud alignment",
            category="ichimoku",
            parameters={
                "conversion_period": self.conversion_period,
                "base_period": self.base_period,
                "leading_span_b_period": self.leading_span_b_period,
                "displacement": self.displacement,
            },
            required_input_columns=("high", "low", "close"),
            output_columns=self._output_columns,
            warmup_period=self.leading_span_b_period + self.displacement,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low", "close"), strict_ohlc=True)
        high = data["high"].astype(np.float64)
        low = data["low"].astype(np.float64)
        close = data["close"].astype(np.float64)

        # 1. Tenkan-sen (Conversion Line): (9-period high + 9-period low) / 2
        conv_high = high.rolling(window=self.conversion_period, min_periods=self.conversion_period).max()
        conv_low = low.rolling(window=self.conversion_period, min_periods=self.conversion_period).min()
        tenkan = (conv_high + conv_low) / 2.0

        # 2. Kijun-sen (Base Line): (26-period high + 26-period low) / 2
        base_high = high.rolling(window=self.base_period, min_periods=self.base_period).max()
        base_low = low.rolling(window=self.base_period, min_periods=self.base_period).min()
        kijun = (base_high + base_low) / 2.0

        # 3. Raw Senkou Span A and B (calculated at bar T)
        raw_senkou_a = (tenkan + kijun) / 2.0

        span_b_high = high.rolling(
            window=self.leading_span_b_period, min_periods=self.leading_span_b_period
        ).max()
        span_b_low = low.rolling(
            window=self.leading_span_b_period, min_periods=self.leading_span_b_period
        ).min()
        raw_senkou_b = (span_b_high + span_b_low) / 2.0

        # 4. Causal Alignment (Look-ahead protection):
        # The cloud at timestamp T is the one projected from (T - displacement).
        # We shift raw spans forward by displacement bars.
        senkou_a = raw_senkou_a.shift(self.displacement)
        senkou_b = raw_senkou_b.shift(self.displacement)

        # 5. Chikou Span:
        # Comparison with past price: Close(T - displacement)
        chikou = close.shift(self.displacement)

        # 6. Derived Features
        cloud_top = np.maximum(senkou_a, senkou_b)
        cloud_bottom = np.minimum(senkou_a, senkou_b)

        # Where cloud is NaN (during warmup), derived features are NaN or False
        valid_cloud = senkou_a.notna() & senkou_b.notna()

        price_above_cloud = pd.Series(
            np.where(valid_cloud, close > cloud_top, np.nan),
            index=data.index,
            dtype=np.float64,
        )
        price_below_cloud = pd.Series(
            np.where(valid_cloud, close < cloud_bottom, np.nan),
            index=data.index,
            dtype=np.float64,
        )
        price_inside_cloud = pd.Series(
            np.where(valid_cloud, (close >= cloud_bottom) & (close <= cloud_top), np.nan),
            index=data.index,
            dtype=np.float64,
        )

        valid_lines = tenkan.notna() & kijun.notna()
        tenkan_above_kijun = pd.Series(
            np.where(valid_lines, tenkan > kijun, np.nan),
            index=data.index,
            dtype=np.float64,
        )
        tenkan_below_kijun = pd.Series(
            np.where(valid_lines, tenkan < kijun, np.nan),
            index=data.index,
            dtype=np.float64,
        )

        cloud_bullish = pd.Series(
            np.where(valid_cloud, senkou_a > senkou_b, np.nan),
            index=data.index,
            dtype=np.float64,
        )
        cloud_bearish = pd.Series(
            np.where(valid_cloud, senkou_a < senkou_b, np.nan),
            index=data.index,
            dtype=np.float64,
        )
        cloud_width = (senkou_a - senkou_b).abs()

        return pd.DataFrame(
            {
                "tenkan": tenkan,
                "kijun": kijun,
                "senkou_a": senkou_a,
                "senkou_b": senkou_b,
                "chikou": chikou,
                "price_above_cloud": price_above_cloud,
                "price_below_cloud": price_below_cloud,
                "price_inside_cloud": price_inside_cloud,
                "tenkan_above_kijun": tenkan_above_kijun,
                "tenkan_below_kijun": tenkan_below_kijun,
                "cloud_bullish": cloud_bullish,
                "cloud_bearish": cloud_bearish,
                "cloud_width": cloud_width,
            },
            index=data.index,
        )
