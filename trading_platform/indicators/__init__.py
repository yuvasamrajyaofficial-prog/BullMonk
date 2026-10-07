"""
BullMonk Quantitative Indicator & Feature Engine.

Provides reusable, deterministic, vectorized technical indicators and quantitative features
calculated on standardized OHLCV and market data structures.

Key subsystems:
- Trend: SMA, EMA, WMA, HMA, ADX, Supertrend
- Momentum: RSI, StochasticOscillator, StochasticRSI, MACD, ROC
- Volatility: ATR, BollingerBands, BollingerBandWidth, HistoricalVolatility
- Volume: OBV, VolumeSMA, VolumeRatio, SessionVWAP, CVDProxy
- Price: Returns, LogReturns, HighLowRange, TrueRange, PercentageChange, RollingHigh, RollingLow
- Session: SessionFeatures
- Ichimoku: IchimokuCloud (Strict causal alignment)
- Options: BlackScholesGreeks, calculate_black_scholes, DeltaTargetOptionSelector
- Pipeline: FeaturePipeline
- Registry: IndicatorRegistry, default_registry
"""

from indicators.base import Indicator, IndicatorMetadata
from indicators.features import FeaturePipeline
from indicators.ichimoku import IchimokuCloud
from indicators.momentum import (
    MACD,
    ROC,
    RSI,
    StochasticOscillator,
    StochasticRSI,
)
from indicators.options import (
    BlackScholesGreeks,
    DeltaTargetOptionSelector,
    StrikeSelectionResult,
    calculate_black_scholes,
)
from indicators.price import (
    HighLowRange,
    LogReturns,
    PercentageChange,
    Returns,
    RollingHigh,
    RollingLow,
    TrueRange,
)
from indicators.registry import IndicatorRegistry, default_registry
from indicators.series import bars_to_dataframe, to_dataframe
from indicators.session import SessionFeatures
from indicators.trend import (
    ADX,
    EMA,
    HMA,
    SMA,
    WMA,
    Supertrend,
)
from indicators.validation import IndicatorValidationError, validate_dataframe
from indicators.volatility import (
    ATR,
    BollingerBands,
    BollingerBandWidth,
    HistoricalVolatility,
)
from indicators.volume import (
    OBV,
    CVDProxy,
    SessionVWAP,
    VolumeRatio,
    VolumeSMA,
)

__all__ = [
    # Base & Validation
    "Indicator",
    "IndicatorMetadata",
    "IndicatorValidationError",
    "validate_dataframe",
    "to_dataframe",
    "bars_to_dataframe",
    # Pipeline & Registry
    "FeaturePipeline",
    "IndicatorRegistry",
    "default_registry",
    # Trend
    "SMA",
    "EMA",
    "WMA",
    "HMA",
    "ADX",
    "Supertrend",
    # Momentum
    "RSI",
    "StochasticOscillator",
    "StochasticRSI",
    "MACD",
    "ROC",
    # Volatility
    "ATR",
    "BollingerBands",
    "BollingerBandWidth",
    "HistoricalVolatility",
    # Volume
    "OBV",
    "VolumeSMA",
    "VolumeRatio",
    "SessionVWAP",
    "CVDProxy",
    # Price
    "Returns",
    "LogReturns",
    "HighLowRange",
    "TrueRange",
    "PercentageChange",
    "RollingHigh",
    "RollingLow",
    # Session
    "SessionFeatures",
    # Ichimoku
    "IchimokuCloud",
    # Options
    "BlackScholesGreeks",
    "StrikeSelectionResult",
    "calculate_black_scholes",
    "DeltaTargetOptionSelector",
]
