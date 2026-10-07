"""
Volume and flow indicators for the BullMonk quantitative engine.

Implements:
- OBV (On-Balance Volume)
- VolumeSMA (Simple Moving Average of Volume)
- VolumeRatio (Current Volume / Volume SMA)
- SessionVWAP (Volume-Weighted Average Price resetting per exchange session)
- CVDProxy (Candle-based Cumulative Volume Delta proxy)

NOTE:
CVDProxy is a candle-derived approximation based on intrabar price displacement
and total volume. It is NOT true exchange-level bid/ask order-flow CVD.
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

from data.sessions import SessionCalendar, get_session_calendar
from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe


def _identify_session_starts(
    timestamps: pd.Series, calendar: Optional[SessionCalendar] = None
) -> np.ndarray:
    """
    Identify boolean indices where a new trading session begins.

    Uses exchange calendar timezone if provided, otherwise uses the timestamp's
    local or UTC date transitions.
    """
    n = len(timestamps)
    if n == 0:
        return np.array([], dtype=bool)

    is_new_session = np.zeros(n, dtype=bool)
    is_new_session[0] = True  # First bar always starts a session

    if n == 1:
        return is_new_session

    if calendar is not None:
        # Convert timestamps to the exchange's local timezone
        tz = calendar.tz
        local_ts = pd.to_datetime(timestamps).dt.tz_convert(tz)
        dates = local_ts.dt.date.values
        is_new_session[1:] = dates[1:] != dates[:-1]
    else:
        # Fallback to date changes in whatever timezone is present
        ts_dt = pd.to_datetime(timestamps)
        try:
            dates = ts_dt.dt.date.values
            is_new_session[1:] = dates[1:] != dates[:-1]
        except Exception:
            is_new_session[1:] = False

    return is_new_session


class OBV(Indicator):
    """
    On-Balance Volume (OBV).
    Measures buying and selling pressure as a cumulative indicator,
    adding volume on up days and subtracting on down days.
    """

    def __init__(self, price_col: str = "close") -> None:
        self.price_col = price_col.lower()
        self._output_col = "obv"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="OBV",
            version="1.0.0",
            description="On-Balance Volume",
            category="volume",
            parameters={"price_col": self.price_col},
            required_input_columns=(self.price_col, "volume"),
            output_columns=(self._output_col,),
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=(self.price_col, "volume"))
        close = data[self.price_col].values.astype(np.float64)
        volume = data["volume"].values.astype(np.float64)
        n = len(data)

        if n == 0:
            return pd.DataFrame({self._output_col: []}, index=data.index)

        direction = np.zeros(n, dtype=np.float64)
        price_diff = np.diff(close)
        direction[1:] = np.where(price_diff > 0, 1.0, np.where(price_diff < 0, -1.0, 0.0))

        obv = np.cumsum(direction * volume)
        return pd.DataFrame({self._output_col: obv}, index=data.index)


class VolumeSMA(Indicator):
    """
    Volume Simple Moving Average.
    """

    def __init__(self, period: int = 20) -> None:
        if period <= 0:
            raise ValueError(f"period must be > 0, got {period}")
        self.period = period
        self._output_col = f"volume_sma_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="VolumeSMA",
            version="1.0.0",
            description=f"Volume Simple Moving Average ({self.period})",
            category="volume",
            parameters={"period": self.period},
            required_input_columns=("volume",),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("volume",))
        vol = data["volume"].astype(np.float64)
        result = vol.rolling(window=self.period, min_periods=self.period).mean()
        return pd.DataFrame({self._output_col: result}, index=data.index)


class VolumeRatio(Indicator):
    """
    Volume Ratio.
    Calculates the ratio of current bar volume to its historical moving average.
    Values > 1.0 indicate above-average volume activity.
    """

    def __init__(self, period: int = 20) -> None:
        if period <= 0:
            raise ValueError(f"period must be > 0, got {period}")
        self.period = period
        self._output_col = f"volume_ratio_{self.period}"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="VolumeRatio",
            version="1.0.0",
            description=f"Volume Ratio (Volume / VolumeSMA_{self.period})",
            category="volume",
            parameters={"period": self.period},
            required_input_columns=("volume",),
            output_columns=(self._output_col,),
            warmup_period=self.period,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(data, required_columns=("volume",))
        vol = data["volume"].astype(np.float64)
        vol_sma = vol.rolling(window=self.period, min_periods=self.period).mean()
        ratio = vol / vol_sma.replace(0, np.nan)
        return pd.DataFrame({self._output_col: ratio}, index=data.index)


class SessionVWAP(Indicator):
    """
    Session-aware Volume Weighted Average Price (VWAP).
    Resets at the start of each calendar trading session.
    Works seamlessly across NSE, 24/7 continuous crypto, and global forex markets.
    """

    def __init__(
        self,
        calendar: Optional[SessionCalendar] = None,
        include_deviation: bool = False,
    ) -> None:
        self.calendar = calendar
        self.include_deviation = include_deviation
        self._vwap_col = "vwap"
        self._dev_col = "vwap_deviation"

    @property
    def metadata(self) -> IndicatorMetadata:
        cols = (self._vwap_col, self._dev_col) if self.include_deviation else (self._vwap_col,)
        return IndicatorMetadata(
            name="SessionVWAP",
            version="1.0.0",
            description="Session-aware Volume Weighted Average Price",
            category="volume",
            parameters={
                "calendar": type(self.calendar).__name__ if self.calendar else "None",
                "include_deviation": self.include_deviation,
            },
            required_input_columns=("high", "low", "close", "volume", "timestamp"),
            output_columns=cols,
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        validate_dataframe(
            data,
            required_columns=("high", "low", "close", "volume", "timestamp"),
            strict_ohlc=True,
        )
        high = data["high"].values.astype(np.float64)
        low = data["low"].values.astype(np.float64)
        close = data["close"].values.astype(np.float64)
        volume = data["volume"].values.astype(np.float64)
        timestamps = data["timestamp"]
        n = len(data)

        if n == 0:
            cols = {self._vwap_col: []}
            if self.include_deviation:
                cols[self._dev_col] = []
            return pd.DataFrame(cols, index=data.index)

        typical_price = (high + low + close) / 3.0
        pv = typical_price * volume

        is_new_session = _identify_session_starts(timestamps, self.calendar)

        vwap = np.zeros(n, dtype=np.float64)
        cum_pv = 0.0
        cum_vol = 0.0

        for i in range(n):
            if is_new_session[i]:
                cum_pv = pv[i]
                cum_vol = volume[i]
            else:
                cum_pv += pv[i]
                cum_vol += volume[i]

            if cum_vol > 0:
                vwap[i] = cum_pv / cum_vol
            else:
                vwap[i] = typical_price[i]

        res_dict = {self._vwap_col: vwap}
        if self.include_deviation:
            deviation = np.where(vwap > 0, ((close - vwap) / vwap) * 100.0, 0.0)
            res_dict[self._dev_col] = deviation

        return pd.DataFrame(res_dict, index=data.index)


class CVDProxy(Indicator):
    """
    Candle-based Cumulative Volume Delta (CVD) Proxy.

    Formula:
        candle_delta = Volume * (2 * (Close - Low) / (High - Low) - 1)
        When High == Low, candle_delta = 0.0 (prevents division by zero).

    Provides:
    - candle_delta: Single-bar estimated net delta
    - cumulative_delta: All-time running cumulative delta
    - session_cumulative_delta: Running cumulative delta resetting per session

    IMPORTANT ARCHITECTURAL DISCLAIMER:
    This is a candle-derived synthetic proxy based on intrabar price location
    and total volume. It is NOT true exchange-level bid/ask order-flow CVD.
    """

    def __init__(self, calendar: Optional[SessionCalendar] = None) -> None:
        self.calendar = calendar
        self._candle_delta_col = "candle_delta"
        self._cum_delta_col = "cumulative_delta"
        self._session_cum_delta_col = "session_cumulative_delta"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="CVDProxy",
            version="1.0.0",
            description="Candle-derived CVD proxy (not true tick order-flow)",
            category="volume",
            parameters={"calendar": type(self.calendar).__name__ if self.calendar else "None"},
            required_input_columns=("high", "low", "close", "volume"),
            output_columns=(
                self._candle_delta_col,
                self._cum_delta_col,
                self._session_cum_delta_col,
            ),
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        req_cols = ["high", "low", "close", "volume"]
        if "timestamp" in data.columns:
            req_cols.append("timestamp")

        validate_dataframe(data, required_columns=req_cols, strict_ohlc=True)
        high = data["high"].values.astype(np.float64)
        low = data["low"].values.astype(np.float64)
        close = data["close"].values.astype(np.float64)
        volume = data["volume"].values.astype(np.float64)
        n = len(data)

        if n == 0:
            return pd.DataFrame(
                {
                    self._candle_delta_col: [],
                    self._cum_delta_col: [],
                    self._session_cum_delta_col: [],
                },
                index=data.index,
            )

        hl_range = high - low
        # Handle High == Low safely without division-by-zero
        with np.errstate(divide="ignore", invalid="ignore"):
            delta_ratio = np.where(hl_range > 0, 2.0 * ((close - low) / hl_range) - 1.0, 0.0)

        candle_delta = volume * delta_ratio
        cum_delta = np.cumsum(candle_delta)

        # Calculate session cumulative delta if timestamp exists
        session_cum_delta = np.zeros(n, dtype=np.float64)
        if "timestamp" in data.columns:
            is_new_session = _identify_session_starts(data["timestamp"], self.calendar)
            current_session_sum = 0.0
            for i in range(n):
                if is_new_session[i]:
                    current_session_sum = candle_delta[i]
                else:
                    current_session_sum += candle_delta[i]
                session_cum_delta[i] = current_session_sum
        else:
            session_cum_delta = cum_delta.copy()

        return pd.DataFrame(
            {
                self._candle_delta_col: candle_delta,
                self._cum_delta_col: cum_delta,
                self._session_cum_delta_col: session_cum_delta,
            },
            index=data.index,
        )
