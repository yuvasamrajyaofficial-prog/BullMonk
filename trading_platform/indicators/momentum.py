"""
Momentum indicators for the BullMonk quantitative engine.

Implements:
- RSI (Relative Strength Index - Wilder's smoothed)
- Stochastic RSI
- Stochastic Oscillator (%K and %D)
- MACD (MACD line, Signal line, MACD Histogram)
- ROC (Rate of Change)
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


class RSI(Indicator):
    """
    Relative Strength Index (RSI).
    Calculates Wilder's smoothed momentum oscillator bound between 0 and 100.
    """

    def __init__(self, period: int = 14, price_col: str = "close") -> None:
        if period <= 1:
            raise ValueError(f"period must be > 1, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"rsi_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="RSI",
            version="1.0.0",
            description=f"Relative Strength Index ({self.period})",
            category="momentum",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period + 1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)
        delta = close.diff()

        gain = delta.clip(lower=0.0)
        loss = (-delta).clip(lower=0.0)

        # Wilder's smoothing: alpha = 1 / period
        alpha = 1.0 / self.period
        avg_gain = gain.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()
        avg_loss = loss.ewm(alpha=alpha, adjust=False, min_periods=self.period).mean()

        total = avg_gain + avg_loss
        # RSI = 100 * (avg_gain / total). If total == 0, RSI = 50.0
        rsi = np.where(total == 0.0, 50.0, 100.0 * (avg_gain / total))
        rsi_series = pd.Series(rsi, index=data.index)

        # Ensure values before warmup are strictly NaN
        rsi_series.iloc[: self.period] = np.nan

        return pd.DataFrame({self._output_col: rsi_series}, index=data.index)


class StochasticOscillator(Indicator):
    """
    Stochastic Oscillator (%K, %D).
    Compares closing price to price range over a given period.
    """

    def __init__(self, k_period: int = 14, d_period: int = 3, slowing: int = 3) -> None:
        if k_period <= 1:
            raise ValueError(f"k_period must be > 1, got {k_period}")
        if d_period < 1 or slowing < 1:
            raise ValueError("d_period and slowing must be >= 1")
        self.k_period = k_period
        self.d_period = d_period
        self.slowing = slowing
        self._k_col = f"stoch_k_{self.k_period}"
        self._d_col = f"stoch_d_{self.d_period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="StochasticOscillator",
            version="1.0.0",
            description=f"Stochastic Oscillator ({self.k_period}, {self.d_period}, {self.slowing})",
            category="momentum",
            parameters={
                "k_period": self.k_period,
                "d_period": self.d_period,
                "slowing": self.slowing,
            },
            required_input_columns=("high", "low", "close"),
            output_columns=(self._k_col, self._d_col),
            warmup_period=self.k_period + self.slowing + self.d_period - 2,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("high", "low", "close"), strict_ohlc=True)
        high = data["high"].astype(np.float64)
        low = data["low"].astype(np.float64)
        close = data["close"].astype(np.float64)

        lowest_low = low.rolling(window=self.k_period, min_periods=self.k_period).min()
        highest_high = high.rolling(window=self.k_period, min_periods=self.k_period).max()
        hl_range = highest_high - lowest_low

        fast_k = 100.0 * (close - lowest_low) / hl_range.replace(0, np.nan)
        if self.slowing > 1:
            slow_k = fast_k.rolling(window=self.slowing, min_periods=self.slowing).mean()
        else:
            slow_k = fast_k

        slow_d = slow_k.rolling(window=self.d_period, min_periods=self.d_period).mean()

        return pd.DataFrame({self._k_col: slow_k, self._d_col: slow_d}, index=data.index)


class StochasticRSI(Indicator):
    """
    Stochastic RSI.
    Applies Stochastic formula to RSI values rather than standard prices.
    """

    def __init__(
        self,
        rsi_period: int = 14,
        stoch_period: int = 14,
        k_period: int = 3,
        d_period: int = 3,
    ) -> None:
        self.rsi_period = rsi_period
        self.stoch_period = stoch_period
        self.k_period = k_period
        self.d_period = d_period
        self._k_col = f"stoch_rsi_k_{self.stoch_period}"
        self._d_col = f"stoch_rsi_d_{self.d_period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="StochasticRSI",
            version="1.0.0",
            description=f"Stochastic RSI ({self.rsi_period}, {self.stoch_period}, {self.k_period}, {self.d_period})",
            category="momentum",
            parameters={
                "rsi_period": self.rsi_period,
                "stoch_period": self.stoch_period,
                "k_period": self.k_period,
                "d_period": self.d_period,
            },
            required_input_columns=("close",),
            output_columns=(self._k_col, self._d_col),
            warmup_period=self.rsi_period + self.stoch_period + self.k_period + self.d_period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("close",))
        rsi_calc = RSI(period=self.rsi_period)
        rsi_df = rsi_calc.calculate(data)
        rsi_series = rsi_df[f"rsi_{self.rsi_period}"]

        min_rsi = rsi_series.rolling(window=self.stoch_period, min_periods=self.stoch_period).min()
        max_rsi = rsi_series.rolling(window=self.stoch_period, min_periods=self.stoch_period).max()
        rsi_range = max_rsi - min_rsi

        stoch_rsi = (rsi_series - min_rsi) / rsi_range.replace(0, np.nan)
        k = stoch_rsi.rolling(window=self.k_period, min_periods=self.k_period).mean() * 100.0
        d = k.rolling(window=self.d_period, min_periods=self.d_period).mean()

        return pd.DataFrame({self._k_col: k, self._d_col: d}, index=data.index)


class MACD(Indicator):
    """
    Moving Average Convergence Divergence (MACD).
    Calculates MACD line (Fast EMA - Slow EMA), Signal line (EMA of MACD),
    and Histogram (MACD - Signal).
    """

    def __init__(
        self,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9,
        price_col: str = "close",
    ) -> None:
        if fast_period >= slow_period:
            raise ValueError(f"fast_period ({fast_period}) must be < slow_period ({slow_period})")
        if signal_period < 1:
            raise ValueError(f"signal_period must be >= 1, got {signal_period}")
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.price_col = price_col.lower()
        self._macd_col = f"macd_{self.fast_period}_{self.slow_period}"
        self._signal_col = f"macd_signal_{self.signal_period}"
        self._hist_col = f"macd_hist_{self.fast_period}_{self.slow_period}_{self.signal_period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="MACD",
            version="1.0.0",
            description=f"MACD ({self.fast_period}, {self.slow_period}, {self.signal_period})",
            category="momentum",
            parameters={
                "fast_period": self.fast_period,
                "slow_period": self.slow_period,
                "signal_period": self.signal_period,
                "price_col": self.price_col,
            },
            required_input_columns=(self.price_col,),
            output_columns=(self._macd_col, self._signal_col, self._hist_col),
            warmup_period=self.slow_period + self.signal_period - 1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)

        fast_ema = close.ewm(span=self.fast_period, adjust=False, min_periods=self.fast_period).mean()
        slow_ema = close.ewm(span=self.slow_period, adjust=False, min_periods=self.slow_period).mean()

        macd_line = fast_ema - slow_ema
        signal_line = macd_line.ewm(
            span=self.signal_period, adjust=False, min_periods=self.signal_period
        ).mean()
        hist = macd_line - signal_line

        return pd.DataFrame(
            {
                self._macd_col: macd_line,
                self._signal_col: signal_line,
                self._hist_col: hist,
            },
            index=data.index,
        )


class ROC(Indicator):
    """
    Rate of Change (ROC).
    Measures percentage change in price from `period` bars ago to current bar.
    """

    def __init__(self, period: int = 12, price_col: str = "close") -> None:
        if period < 1:
            raise ValueError(f"period must be >= 1, got {period}")
        self.period = period
        self.price_col = price_col.lower()
        self._output_col = f"roc_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="ROC",
            version="1.0.0",
            description=f"Rate of Change ({self.period})",
            category="momentum",
            parameters={"period": self.period, "price_col": self.price_col},
            required_input_columns=(self.price_col,),
            output_columns=(self._output_col,),
            warmup_period=self.period + 1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col,))
        close = data[self.price_col].astype(np.float64)
        prev = close.shift(self.period)
        roc = 100.0 * (close - prev) / prev.replace(0, np.nan)
        return pd.DataFrame({self._output_col: roc}, index=data.index)
