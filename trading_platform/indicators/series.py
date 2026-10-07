"""
Series conversion and data formatting utilities for indicators.

Handles conversion between lists of OHLCVBar domain models and normalized
pandas DataFrames suitable for vectorized quantitative calculations.
"""

from __future__ import annotations

from typing import Iterable, Sequence, Union
import numpy as np
import pandas as pd

from core.models import OHLCVBar


def bars_to_dataframe(bars: Sequence[OHLCVBar]) -> pd.DataFrame:
    """
    Convert a sequence of OHLCVBar domain models to a normalized pandas DataFrame.

    Ensures:
    - Standard lowercase column names: ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    - Appropriate float64 dtypes for mathematical vectorization
    - Timezone-aware timestamp column preserved
    - Monotonically increasing time order
    """
    if not bars:
        return pd.DataFrame(
            columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

    records = [
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

    df = pd.DataFrame.from_records(records)
    # Ensure float64 numeric types
    for col in ("open", "high", "low", "close", "volume"):
        df[col] = df[col].astype(np.float64)

    return df


def to_dataframe(data: Union[pd.DataFrame, Sequence[OHLCVBar]]) -> pd.DataFrame:
    """
    Normalize input data into a clean, unmutated pandas DataFrame.

    If given a DataFrame, creates a shallow copy with standardized lowercase column names.
    If given a sequence of OHLCVBars, converts it using bars_to_dataframe().
    """
    if isinstance(data, pd.DataFrame):
        df = data.copy()
        # Normalize column names to lowercase
        df.columns = [str(c).lower().strip() for c in df.columns]
        return df
    return bars_to_dataframe(data)
