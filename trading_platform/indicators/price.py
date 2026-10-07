"""
Price action and return features for the BullMonk quantitative engine.

Implements:
- Returns (Simple arithmetic price returns)
- LogReturns (Logarithmic price returns)
- HighLowRange (Intrabar High - Low spread)
- TrueRange (Wilder's True Range)
- PercentageChange (Intrabar (Close - Open) / Open * 100)
- RollingHigh (Rolling highest high over N periods)
- RollingLow (Rolling lowest low over N periods)
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


class Returns(Indicator):
    """
    Simple arithmetic returns: (P_t - P_{t-k}) / P_{t-k}.
    """

    def __init__(self, period: int = 1, price_col: str = "close") -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"returns_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="Returns",
            version="1.0.0",
            description=f"Simple Returns ({self.period})",
            category="price",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)
        prev = close.shift(self.period)
        ret = (close - prev) / prev.replace(0, np.nan)
        return pd.DataFrame({self._output_col: ret}, index=data.index)


class LogReturns(Indicator):
    """
    Logarithmic returns: ln(P_t / P_{t-k}).
    """

    def __init__(self, period: int = 1, price_col: str = "close") -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"log_returns_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="LogReturns",
            version="1.0.0",
            description=f"Logarithmic Returns ({self.period})",
            category="price",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)
        prev = close.shift(self.period)
        log_ret = np.log(close / prev.replace(0, np.nan))
        return pd.DataFrame({self._output_col: log_ret}, index=data.index)


class HighLowRange(Indicator):
    """
    Intrabar High - Low price range.
    """

    def __init__(self) -> None:
        self._output_col = "hl_range"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="HighLowRange",
            version="1.0.0",
            description="Intrabar High-Low price range",
            category="price",
            parameters={},
            required_input_columns=("high", "low"),
            output_columns=(self._output_col,),
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low"), strict_ohlc=True)
        hl = data["high"].astype(np.float64) - data["low"].astype(np.float64)
        return pd.DataFrame({self._output_col: hl}, index=data.index)


class TrueRange(Indicator):
    """
    Wilder's True Range (TR): max(H - L, |H - C_{prev}|, |L - C_{prev}|).
    """

    def __init__(self) -> None:
        self._output_col = "true_range"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="TrueRange",
            version="1.0.0",
            description="Wilder's True Range",
            category="price",
            parameters={},
            required_input_columns=("high", "low", "close"),
            output_columns=(self._output_col,),
            warmup_period=1,
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
        # First bar has no prev_close, so true range is simply High - Low
        tr.iloc[0] = high.iloc[0] - low.iloc[0]

        return pd.DataFrame({self._output_col: tr}, index=data.index)


class PercentageChange(Indicator):
    """
    Intrabar percentage change: ((Close - Open) / Open) * 100.
    """

    def __init__(self) -> None:
        self._output_col = "pct_change"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="PercentageChange",
            version="1.0.0",
            description="Intrabar percentage change ((Close - Open) / Open * 100)",
            category="price",
            parameters={},
            required_input_columns=("open", "close"),
            output_columns=(self._output_col,),
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("open", "close"))
        op = data["open"].astype(np.float64)
        cl = data["close"].astype(np.float64)
        pct = 100.0 * (cl - op) / op.replace(0, np.nan)
        return pd.DataFrame({self._output_col: pct}, index=data.index)


class RollingHigh(Indicator):
    """
    Rolling highest high over a given period window.
    """

    def __init__(self, period: int = 20) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self.period = period
        self._output_col = f"rolling_high_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="RollingHigh",
            version="1.0.0",
            description=f"Rolling Highest High ({self.period})",
            category="price",
            parameters={"period": self.period},
            required_input_columns=("high",),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high",))
        result = data["high"].astype(np.float64).rolling(window=self.period, min_periods=self.period).max()
        return pd.DataFrame({self._output_col: result}, index=data.index)


class RollingLow(Indicator):
    """
    Rolling lowest low over a given period window.
    """

    def __init__(self, period: int = 20) -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self.period = period
        self._output_col = f"rolling_low_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="RollingLow",
            version="1.0.0",
            description=f"Rolling Lowest Low ({self.period})",
            category="price",
            parameters={"period": self.period},
            required_input_columns=("low",),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("low",))
        result = data["low"].astype(np.float64).rolling(window=self.period, min_periods=self.period).min()
        return pd.DataFrame({self._output_col: result}, index=data.index)
