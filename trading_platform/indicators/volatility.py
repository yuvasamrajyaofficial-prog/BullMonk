"""
Volatility indicators for the BullMonk quantitative engine.

Implements:
- ATR (Average True Range - Wilder's smoothed)
- Bollinger Bands (Upper, Middle, Lower, Bandwidth, %B)
- Bollinger Band Width (standalone)
- Historical Volatility (Annualized rolling log-returns volatility)
"""

from __future__ import annotations

import math
from typing import Any, Optional
import numpy as np
import pandas as pd

from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


class ATR(Indicator):
    """
    Average True Range (ATR).
    Calculates Wilder's smoothed average true range to quantify asset volatility.
    """

    def __init__(self, period: int = 14) -> None:
        if period <= 0:
            raise ValueError(f"period must be > 0, got {period}")
        self.period = period
        self._output_col = f"atr_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ATR",
            version="1.0.0",
            description=f"Average True Range ({self.period})",
            category="volatility",
            parameters={"period": self.period},
            required_input_columns=("high", "low", "close"),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low", "close"), strict_ohlc=True)
        high = data["high"].astype(np.float64)
        low = data["low"].astype(np.float64)
        close = data["close"].astype(np.float64)

        prev_close = close.shift(1)
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Wilder's smoothing: alpha = 1 / period
        atr = tr.ewm(alpha=1.0 / self.period, adjust=False, min_periods=self.period).mean()

        return pd.DataFrame({self._output_col: atr}, index=data.index)


class BollingerBands(Indicator):
    """
    Bollinger Bands (Upper, Middle, Lower, Bandwidth, %B).
    Calculates volatility bands around a simple moving average.
    """

    def __init__(
        self,
        period: int = 20,
        std_dev: float = 2.0,
        price_col: str = "close",
    ) -> None:
        if period <= 1:
            raise ValueError(f"period must be > 1, got {period}")
        if std_dev <= 0:
            raise ValueError(f"std_dev must be > 0, got {std_dev}")
        self.period = period
        self.std_dev = float(std_dev)
        self.price_col = price_col.lower()

        self._upper_col = f"bb_upper_{self.period}_{self.std_dev}"
        self._mid_col = f"bb_middle_{self.period}"
        self._lower_col = f"bb_lower_{self.period}_{self.std_dev}"
        self._width_col = f"bb_width_{self.period}_{self.std_dev}"
        self._pct_b_col = f"bb_percent_b_{self.period}_{self.std_dev}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="BollingerBands",
            version="1.0.0",
            description=f"Bollinger Bands (period={self.period}, std={self.std_dev})",
            category="volatility",
            parameters={
                "period": self.period,
                "std_dev": self.std_dev,
                "price_col": self.price_col,
            },
            required_input_columns=(self.price_col,),
            output_columns=(
                self._upper_col,
                self._mid_col,
                self._lower_col,
                self._width_col,
                self._pct_b_col,
            ),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        series = data[self.price_col].astype(np.float64)

        middle = series.rolling(window=self.period, min_periods=self.period).mean()
        std = series.rolling(window=self.period, min_periods=self.period).std(ddof=0)

        upper = middle + self.std_dev * std
        lower = middle - self.std_dev * std
        width = (upper - lower) / middle.replace(0, np.nan)
        band_diff = upper - lower
        percent_b = (series - lower) / band_diff.replace(0, np.nan)

        return pd.DataFrame(
            {
                self._upper_col: upper,
                self._mid_col: middle,
                self._lower_col: lower,
                self._width_col: width,
                self._pct_b_col: percent_b,
            },
            index=data.index,
        )


class BollingerBandWidth(Indicator):
    """
    Bollinger Band Width indicator.
    Measures the normalized distance between upper and lower Bollinger Bands:
    (Upper - Lower) / Middle
    """

    def __init__(self, period: int = 20, std_dev: float = 2.0, price_col: str = "close") -> None:
        self.period = period
        self.std_dev = float(std_dev)
        self.price_col = price_col.lower()
        self._output_col = f"bb_width_{self.period}_{self.std_dev}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="BollingerBandWidth",
            version="1.0.0",
            description=f"Bollinger Band Width ({self.period}, {self.std_dev})",
            category="volatility",
            parameters={"period": self.period, "std_dev": self.std_dev, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        bb = BollingerBands(period=self.period, std_dev=self.std_dev, price_col=self.price_col)
        df_bb = bb.calculate(data)
        return pd.DataFrame({self._output_col: df_bb[self._output_col]}, index=data.index)


class HistoricalVolatility(Indicator):
    """
    Annualized Historical Volatility (HV).
    Calculates the standard deviation of logarithmic returns annualized across trading days.
    """

    def __init__(
        self,
        period: int = 20,
        trading_days: int = 252,
        price_col: str = "close",
    ) -> None:
        if period <= 1:
            raise ValueError(f"period must be > 1, got {period}")
        if trading_days <= 0:
            raise ValueError(f"trading_days must be > 0, got {trading_days}")
        self.period = period
        self.trading_days = trading_days
        self.price_col = price_col.lower()
        self._output_col = f"hist_vol_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="HistoricalVolatility",
            version="1.0.0",
            description=f"Annualized Historical Volatility ({self.period})",
            category="volatility",
            parameters={
                "period": self.period,
                "trading_days": self.trading_days,
                "price_col": self.price_col,
            },
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period + 1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)
        log_ret = np.log(close / close.shift(1).replace(0, np.nan))

        rolling_std = log_ret.rolling(window=self.period, min_periods=self.period).std(ddof=1)
        annualized_vol = rolling_std * math.sqrt(self.trading_days) * 100.0

        return pd.DataFrame({self._output_col: annualized_vol}, index=data.index)
