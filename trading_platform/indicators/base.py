"""
Base indicator interfaces and contracts for the BullMonk quantitative engine.

Defines the core `Indicator` protocol, `IndicatorMetadata`, and standard interfaces
used across backtesting, research, paper trading, and live execution.
Indicators are deterministic, stateless, and do not contain strategy-specific entry/exit logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, Sequence
import pandas as pd


@dataclass(frozen=True)
class IndicatorMetadata:
    """
    Metadata describing an indicator's characteristics, input requirements,
    and output schema.
    """

    name: str
    version: str
    description: str
    category: str  # trend, momentum, volatility, volume, price, session, ichimoku, options
    parameters: dict[str, Any] = field(default_factory=dict)
    required_input_columns: tuple[str, ...] = ("close",)
    output_columns: tuple[str, ...] = field(default_factory=tuple)
    warmup_period: int = 0


class Indicator(ABC):
    """
    Abstract base class for all quantitative indicators and feature calculators.

    Guarantees:
    - Pure, deterministic calculation (no mutable global state).
    - Preserves timestamp and index integrity.
    - Never mutates the caller's DataFrame.
    - Strict warmup handling (missing values returned as NaN, never fake zeros).
    - Zero look-ahead bias (only data available at or before timestamp T is used).
    """

    @property
    @abstractmethod
    def metadata(self) -> IndicatorMetadata:
        """Return the indicator's metadata and specification."""
        ...

    @property
    def name(self) -> str:
        """Convenience property for indicator name."""
        return self.metadata.name

    @property
    def warmup_period(self) -> int:
        """Number of historical bars required before values become mathematically valid."""
        return self.metadata.warmup_period

    @property
    def required_input_columns(self) -> tuple[str, ...]:
        """Names of required columns in the input DataFrame."""
        return self.metadata.required_input_columns

    @property
    def output_columns(self) -> tuple[str, ...]:
        """Names of columns produced by calculate()."""
        return self.metadata.output_columns

    @abstractmethod
    def calculate(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate indicator values from normalized market data.

        Args:
            data: pd.DataFrame with required OHLCV columns. Must be sorted chronologically.

        Returns:
            pd.DataFrame containing calculated feature columns with the same index as input.
        """
        ...

    def __repr__(self) -> str:
        meta = self.metadata
        param_str = ", ".join(f"{k}={v}" for k, v in meta.parameters.items())
        return f"{self.__class__.__name__}({param_str})"
