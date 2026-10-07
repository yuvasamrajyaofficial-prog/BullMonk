"""
Trend indicators for the BullMonk quantitative engine.

Implements:
- SMA (Simple Moving Average)
- EMA (Exponential Moving Average)
- WMA (Weighted Moving Average)
- HMA (Hull Moving Average)
- ADX (Average Directional Index with +DI and -DI)
- Supertrend (Direction, Upper Band, Lower Band, Supertrend Value)
"""

from __future__ import annotations

import math
from typing import Any, Optional
import numpy as np
import pandas as pd

from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


def _calc_wma(series: pd.Series, period: int) -> pd.Series:
    """Helper to compute Weighted Moving Average on a pandas Series."""
    weights = np.arange(1, period + 1, dtype=np.float64)
    sum_weights = weights.sum()

    def wma_calc(x: np.ndarray) -> float:
        return float(np.dot(x, weights) / sum_weights)

    return series.rolling(window=period, min_periods=period).apply(wma_calc, raw=True)


class SMA(Indicator):
    """
    Simple Moving Average (SMA).
    Calculates the unweighted mean of the previous `period` bars.
    """

    def __init__(self, period: int = 14, price_col: str = "close") -> None:
        if period <= 0:
            raise ValueError(f"period must be a positive integer, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"sma_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="SMA",
            version="1.0.0",
            description=f"Simple Moving Average ({self.period})",
            category="trend",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        series = data[self.price_col].astype(np.float64)
        result = series.rolling(window=self.period, min_periods=self.period).mean()
        return pd.DataFrame({self._output_col: result}, index=data.index)


class EMA(Indicator):
    """
    Exponential Moving Average (EMA).
    Applies weighting factors which decrease exponentially.
    Strictly preserves NaN during the initial warmup period.
    """

    def __init__(self, period: int = 20, price_col: str = "close", adjust: bool = False) -> None:
        if period <= 0:
            raise ValueError(f"period must be a positive integer, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self.adjust = adjust
        self._output_col = f"ema_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="EMA",
            version="1.0.0",
            description=f"Exponential Moving Average ({self.period})",
            category="trend",
            parameters={"period": self.period, "price_col": self.price_col, "adjust": self.adjust},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        series = data[self.price_col].astype(np.float64)
        # min_periods=period ensures that earlier values are returned as NaN
        result = series.ewm(span=self.period, adjust=self.adjust, min_periods=self.period).mean()
        return pd.DataFrame({self._output_col: result}, index=data.index)


class WMA(Indicator):
    """
    Weighted Moving Average (WMA).
    Allocates proportionally heavier weighting to the most recent data points.
    """

    def __init__(self, period: int = 14, price_col: str = "close") -> None:
        if period <= 0:
            raise ValueError(f"period must be a positive integer, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"wma_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="WMA",
            version="1.0.0",
            description=f"Weighted Moving Average ({self.period})",
            category="trend",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        series = data[self.price_col].astype(np.float64)
        result = _calc_wma(series, self.period)
        return pd.DataFrame({self._output_col: result}, index=data.index)


class HMA(Indicator):
    """
    Hull Moving Average (HMA).
    Extremely fast and smooth moving average created by Alan Hull.
    Formula:
        WMA(2 * WMA(n/2) - WMA(n), sqrt(n))
    """

    def __init__(self, period: int = 14, price_col: str = "close") -> None:
        if period < 4:
            raise ValueError(f"period must be >= 4 for HMA, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"hma_{self.period}"
        self._sqrt_period = int(math.sqrt(self.period))

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="HMA",
            version="1.0.0",
            description=f"Hull Moving Average ({self.period})",
            category="trend",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period + self._sqrt_period - 1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        series = data[self.price_col].astype(np.float64)
        half_period = max(1, self.period // 2)

        wma_half = _calc_wma(series, half_period)
        wma_full = _calc_wma(series, self.period)
        diff = 2.0 * wma_half - wma_full

        result = _calc_wma(diff, self._sqrt_period)
        return pd.DataFrame({self._output_col: result}, index=data.index)


class ADX(Indicator):
    """
    Average Directional Index (ADX) with +DI and -DI.
    Developed by J. Welles Wilder to quantify trend strength regardless of direction.
    Uses Wilder's Exponential Smoothing (alpha = 1 / period).
    """

    def __init__(self, period: int = 14) -> None:
        if period <= 1:
            raise ValueError(f"period must be > 1, got {period}")
        self.period = period
        self._adx_col = f"adx_{self.period}"
        self._plus_di_col = f"plus_di_{self.period}"
        self._minus_di_col = f"minus_di_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ADX",
            version="1.0.0",
            description=f"Average Directional Index ({self.period})",
            category="trend",
            parameters={"period": self.period},
            required_input_columns=("high", "low", "close"),
            output_columns=(self._adx_col, self._plus_di_col, self._minus_di_col),
            warmup_period=2 * self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low", "close"), strict_ohlc=True)
        high = data["high"].astype(np.float64)
        low = data["low"].astype(np.float64)
        close = data["close"].astype(np.float64)

        prev_close = close.shift(1)
        prev_high = high.shift(1)
        prev_low = low.shift(1)

        # True Range
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        up_move = high - prev_high
        down_move = prev_low - low

        plus_dm = pd.Series(
            np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
            index=data.index,
        )
        minus_dm = pd.Series(
            np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
            index=data.index,
        )

        # Wilder's smoothing: alpha = 1 / period
        alpha = 1.0 / self.period
        atr_smooth = tr.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()
        plus_dm_smooth = plus_dm.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()
        minus_dm_smooth = minus_dm.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()

        # +DI and -DI
        plus_di = 100.0 * (plus_dm_smooth / atr_smooth.replace(0, np.nan))
        minus_di = 100.0 * (minus_dm_smooth / atr_smooth.replace(0, np.nan))

        # Directional Index DX
        di_sum = plus_di + minus_di
        di_diff = (plus_di - minus_di).abs()
        dx = 100.0 * (di_diff / di_sum.replace(0, np.nan))

        # ADX: Wilder's smoothing of DX
        adx = dx.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()

        return pd.DataFrame(
            {
                self._adx_col: adx,
                self._plus_di_col: plus_di,
                self._minus_di_col: minus_di,
            },
            index=data.index,
        )


class Supertrend(Indicator):
    """
    Supertrend Indicator.
    Generates trailing trend stop levels and direction (+1 bullish, -1 bearish)
    based on ATR volatility bands.
    """

    def __init__(self, period: int = 10, multiplier: float = 3.0) -> None:
        if period <= 1:
            raise ValueError(f"period must be > 1, got {period}")
        if multiplier <= 0:
            raise ValueError(f"multiplier must be > 0, got {multiplier}")
        self.period = period
        self.multiplier = float(multiplier)
        self._st_col = f"supertrend_{self.period}_{self.multiplier}"
        self._dir_col = f"supertrend_direction_{self.period}_{self.multiplier}"
        self._upper_col = f"supertrend_upper_{self.period}_{self.multiplier}"
        self._lower_col = f"supertrend_lower_{self.period}_{self.multiplier}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="Supertrend",
            version="1.0.0",
            description=f"Supertrend (period={self.period}, mult={self.multiplier})",
            category="trend",
            parameters={"period": self.period, "multiplier": self.multiplier},
            required_input_columns=("high", "low", "close"),
            output_columns=(self._st_col, self._dir_col, self._upper_col, self._lower_col),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low", "close"), strict_ohlc=True)
        high = data["high"].values.astype(np.float64)
        low = data["low"].values.astype(np.float64)
        close = data["close"].values.astype(np.float64)
        n = len(data)

        # 1. Calculate True Range and ATR
        prev_close = np.roll(close, 1)
        prev_close[0] = close[0]

        tr1 = high - low
        tr2 = np.abs(high - prev_close)
        tr3 = np.abs(low - prev_close)
        tr = np.maximum(tr1, np.maximum(tr2, tr3))

        # Wilder's smoothed ATR
        atr_series = pd.Series(tr).ewm(
            alpha=1.0 / self.period, adjust=False, min_periods=self.period
        ).mean().values

        hl2 = (high + low) / 2.0
        basic_upper = hl2 + self.multiplier * atr_series
        basic_lower = hl2 - self.multiplier * atr_series

        final_upper = np.full(n, np.nan, dtype=np.float64)
        final_lower = np.full(n, np.nan, dtype=np.float64)
        supertrend = np.full(n, np.nan, dtype=np.float64)
        direction = np.full(n, np.nan, dtype=np.float64)

        # Iterate forward strictly with no look-ahead
        for i in range(self.period - 1, n):
            if i == self.period - 1:
                final_upper[i] = basic_upper[i]
                final_lower[i] = basic_lower[i]
                direction[i] = 1.0 if close[i] >= basic_lower[i] else -1.0
                supertrend[i] = final_lower[i] if direction[i] == 1.0 else final_upper[i]
                continue

            # Upper Band logic
            if (basic_upper[i] < final_upper[i - 1]) or (close[i - 1] > final_upper[i - 1]):
                final_upper[i] = basic_upper[i]
            else:
                final_upper[i] = final_upper[i - 1]

            # Lower Band logic
            if (basic_lower[i] > final_lower[i - 1]) or (close[i - 1] < final_lower[i - 1]):
                final_lower[i] = basic_lower[i]
            else:
                final_lower[i] = final_lower[i - 1]

            # Direction logic
            prev_dir = direction[i - 1]
            if prev_dir == 1.0:
                if close[i] < final_lower[i]:
                    direction[i] = -1.0
                    supertrend[i] = final_upper[i]
                else:
                    direction[i] = 1.0
                    supertrend[i] = final_lower[i]
            else:  # prev_dir == -1.0
                if close[i] > final_upper[i]:
                    direction[i] = 1.0
                    supertrend[i] = final_lower[i]
                else:
                    direction[i] = -1.0
                    supertrend[i] = final_upper[i]

        return pd.DataFrame(
            {
                self._st_col: supertrend,
                self._dir_col: direction,
                self._upper_col: final_upper,
                self._lower_col: final_lower,
            },
            index=data.index,
        )
