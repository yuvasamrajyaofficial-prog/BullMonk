"""
Session-based indicators and quantitative features for the BullMonk quantitative engine.

Implements:
- SessionOpen, SessionHigh, SessionLow, SessionClose
- OpeningRange (Opening range high and low for first N minutes / bars)
- VWAPDeviation
- SessionFeatures (Composite session analyzer)
"""

from __future__ import annotations

from typing import Any, Optional
import numpy as np
import pandas as pd

from data.sessions import SessionCalendar
from indicators.base import Indicator, IndicatorMetadata
from indicators.validation import validate_dataframe
from indicators.volume import _identify_session_starts, SessionVWAP


class SessionFeatures(Indicator):
    """
    Computes intraday session levels strictly without look-ahead bias:
    - session_open: The open price of the first candle of the active session
    - session_high: Running highest price in the active session up to time T
    - session_low: Running lowest price in the active session up to time T
    - session_close: Current bar close
    - opening_range_high: High of the first N bars/minutes of the session
    - opening_range_low: Low of the first N bars/minutes of the session
    - vwap_deviation: Percentage deviation of Close from running Session VWAP
    """

    def __init__(
        self,
        calendar: Optional[SessionCalendar] = None,
        opening_range_bars: int = 6,  # e.g., 6 x 5-minute bars = 30-min opening range
    ) -> None:
        if opening_range_bars < 1:
            raise ValueError("opening_range_bars must be >= 1")
        self.calendar = calendar
        self.opening_range_bars = opening_range_bars

        self._open_col = "session_open"
        self._high_col = "session_high"
        self._low_col = "session_low"
        self._close_col = "session_close"
        self._or_high_col = f"opening_range_high_{self.opening_range_bars}"
        self._or_low_col = f"opening_range_low_{self.opening_range_bars}"
        self._vwap_dev_col = "vwap_deviation"

    @property
    def metadata(self) -> IndicatorMetadata:
        return IndicatorMetadata(
            name="SessionFeatures",
            version="1.0.0",
            description="Intraday session-relative features and opening range",
            category="session",
            parameters={
                "calendar": type(self.calendar).__name__ if self.calendar else "None",
                "opening_range_bars": self.opening_range_bars,
            },
            required_input_columns=("open", "high", "low", "close", "timestamp"),
            output_columns=(
                self._open_col,
                self._high_col,
                self._low_col,
                self._close_col,
                self._or_high_col,
                self._or_low_col,
                self._vwap_dev_col,
            ),
            warmup_period=1,
        )

    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        req_cols = ["open", "high", "low", "close", "timestamp"]
        has_volume = "volume" in data.columns
        validate_dataframe(data, required_columns=req_cols, strict_ohlc=True)

        opens = data["open"].values.astype(np.float64)
        highs = data["high"].values.astype(np.float64)
        lows = data["low"].values.astype(np.float64)
        closes = data["close"].values.astype(np.float64)
        timestamps = data["timestamp"]
        n = len(data)

        if n == 0:
            return pd.DataFrame(
                {col: [] for col in self.metadata.output_columns}, index=data.index
            )

        is_new_session = _identify_session_starts(timestamps, self.calendar)

        sess_open = np.zeros(n, dtype=np.float64)
        sess_high = np.zeros(n, dtype=np.float64)
        sess_low = np.zeros(n, dtype=np.float64)
        sess_close = closes.copy()

        or_high = np.zeros(n, dtype=np.float64)
        or_low = np.zeros(n, dtype=np.float64)

        cur_open = opens[0]
        cur_high = highs[0]
        cur_low = lows[0]

        session_bar_idx = 0
        cur_or_high = highs[0]
        cur_or_low = lows[0]

        for i in range(n):
            if is_new_session[i]:
                session_bar_idx = 0
                cur_open = opens[i]
                cur_high = highs[i]
                cur_low = lows[i]
                cur_or_high = highs[i]
                cur_or_low = lows[i]
            else:
                session_bar_idx += 1
                cur_high = max(cur_high, highs[i])
                cur_low = min(cur_low, lows[i])

                if session_bar_idx < self.opening_range_bars:
                    cur_or_high = max(cur_or_high, highs[i])
                    cur_or_low = min(cur_or_low, lows[i])

            sess_open[i] = cur_open
            sess_high[i] = cur_high
            sess_low[i] = cur_low
            or_high[i] = cur_or_high
            or_low[i] = cur_or_low

        # VWAP deviation calculation
        if has_volume:
            vwap_indicator = SessionVWAP(calendar=self.calendar)
            vwap_df = vwap_indicator.calculate(data)
            vwap = vwap_df["vwap"].values
            vwap_dev = np.where(vwap > 0, ((closes - vwap) / vwap) * 100.0, 0.0)
        else:
            vwap_dev = np.zeros(n, dtype=np.float64)

        return pd.DataFrame(
            {
                self._open_col: sess_open,
                self._high_col: sess_high,
                self._low_col: sess_low,
                self._close_col: sess_close,
                self._or_high_col: or_high,
                self._or_low_col: or_low,
                self._vwap_dev_col: vwap_dev,
            },
            index=data.index,
        )
