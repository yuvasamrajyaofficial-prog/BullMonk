"""
Input validation utilities for the indicator engine.

Validates DataFrame structure and sanity before executing quantitative calculations:
- Required column presence
- Chronological timestamp ordering (monotonically increasing)
- Timestamp uniqueness (no duplicate timestamps)
- OHLC consistency (High >= Low, High >= Open, High >= Close, Low <= Open, Low <= Close)
- Non-negative volume
- Non-positive price rejection where strictly positive prices are required
"""

from __future__ import annotations

from typing import Sequence
import pandas as pd


class IndicatorValidationError(ValueError):
    """Raised when market data fails quantitative indicator validation checks."""
    pass


def validate_dataframe(
    df: pd.DataFrame,
    required_columns: Sequence[str] = ("close",),
    strict_ohlc: bool = False,
    allow_empty: bool = False,
) -> None:
    """
    Validate that a DataFrame conforms to the input requirements of an indicator.

    Args:
        df: Input pandas DataFrame.
        required_columns: List of column names that must be present in df.
        strict_ohlc: If True, enforces strict high >= low, high >= open, etc.
        allow_empty: If True, empty DataFrames will not raise an error.

    Raises:
        IndicatorValidationError: If any validation rule is violated.
    """
    if df.empty:
        if allow_empty:
            return
        raise IndicatorValidationError("Input DataFrame is empty")

    # 1. Required column presence
    df_cols = set(df.columns)
    missing = [col for col in required_columns if col not in df_cols]
    if missing:
        raise IndicatorValidationError(
            f"Missing required columns: {missing}. Present columns: {list(df.columns)}"
        )

    # 2. Timestamp ordering & uniqueness checks (if timestamp column or DatetimeIndex is present)
    if "timestamp" in df.columns:
        ts_series = df["timestamp"]
        if not ts_series.is_monotonic_increasing:
            raise IndicatorValidationError(
                "Timestamps are unsorted or not strictly monotonically increasing"
            )
        if ts_series.duplicated().any():
            dup_sample = ts_series[ts_series.duplicated()].iloc[0]
            raise IndicatorValidationError(
                f"Duplicate timestamps found in dataset. Example: {dup_sample}"
            )
    elif isinstance(df.index, pd.DatetimeIndex):
        if not df.index.is_monotonic_increasing:
            raise IndicatorValidationError(
                "DatetimeIndex is unsorted or not strictly monotonically increasing"
            )
        if df.index.duplicated().any():
            dup_sample = df.index[df.index.duplicated()][0]
            raise IndicatorValidationError(
                f"Duplicate timestamps found in DatetimeIndex. Example: {dup_sample}"
            )

    # 3. OHLC sanity checks
    has_ohlc = {"open", "high", "low", "close"}.issubset(df_cols)
    if strict_ohlc or (has_ohlc and any(col in required_columns for col in ("open", "high", "low", "close"))):
        if "high" in df_cols and "low" in df_cols:
            invalid_hl = df["high"] < df["low"]
            if invalid_hl.any():
                bad_idx = df.index[invalid_hl][0]
                raise IndicatorValidationError(
                    f"Invalid OHLC relationship: High is strictly less than Low at index {bad_idx}"
                )

        if "high" in df_cols and "open" in df_cols:
            invalid_ho = df["high"] < df["open"]
            if invalid_ho.any():
                bad_idx = df.index[invalid_ho][0]
                raise IndicatorValidationError(
                    f"Invalid OHLC relationship: High is strictly less than Open at index {bad_idx}"
                )

        if "high" in df_cols and "close" in df_cols:
            invalid_hc = df["high"] < df["close"]
            if invalid_hc.any():
                bad_idx = df.index[invalid_hc][0]
                raise IndicatorValidationError(
                    f"Invalid OHLC relationship: High is strictly less than Close at index {bad_idx}"
                )

        if "low" in df_cols and "open" in df_cols:
            invalid_lo = df["low"] > df["open"]
            if invalid_lo.any():
                bad_idx = df.index[invalid_lo][0]
                raise IndicatorValidationError(
                    f"Invalid OHLC relationship: Low is strictly greater than Open at index {bad_idx}"
                )

        if "low" in df_cols and "close" in df_cols:
            invalid_lc = df["low"] > df["close"]
            if invalid_lc.any():
                bad_idx = df.index[invalid_lc][0]
                raise IndicatorValidationError(
                    f"Invalid OHLC relationship: Low is strictly greater than Close at index {bad_idx}"
                )

    # 4. Negative volume check
    if "volume" in df_cols and "volume" in required_columns:
        if (df["volume"] < 0).any():
            bad_idx = df.index[df["volume"] < 0][0]
            raise IndicatorValidationError(
                f"Negative volume detected at index {bad_idx}"
            )

    # 5. Non-positive price checks on prices if required
    for price_col in ("open", "high", "low", "close"):
        if price_col in required_columns and price_col in df_cols:
            if (df[price_col] <= 0).any():
                bad_idx = df.index[df[price_col] <= 0][0]
                raise IndicatorValidationError(
                    f"Non-positive price ({price_col} <= 0) detected at index {bad_idx}"
                )
