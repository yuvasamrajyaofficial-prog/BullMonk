"""Concrete Quantitative Strategy Library."""

from strategies.library.dual_ema import DualEMAStrategy
from strategies.library.opening_range_breakout import OpeningRangeBreakoutStrategy
from strategies.library.bollinger_reversion import BollingerReversionStrategy

__all__ = [
    "DualEMAStrategy",
    "OpeningRangeBreakoutStrategy",
    "BollingerReversionStrategy",
]
