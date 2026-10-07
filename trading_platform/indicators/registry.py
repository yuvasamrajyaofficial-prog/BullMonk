"""
Indicator registry and discovery system for the BullMonk quantitative engine.

Allows programmatic lookup, dynamic instantiation, and inspection of indicators.
Serves as the foundation for future visual Strategy Builder and AI strategy generation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Type
from indicators.base import Indicator, IndicatorMetadata


class IndicatorRegistry:
    """
    Central registry for quantitative indicators and feature generators.
    """

    def __init__(self) -> None:
        self._registry: Dict[str, Type[Indicator]] = {}
        self._aliases: Dict[str, str] = {}

    def register(
        self,
        name: str,
        indicator_cls: Type[Indicator],
        aliases: Optional[list[str]] = None,
    ) -> None:
        """
        Register an indicator class by canonical name and optional aliases.
        """
        canonical = name.upper().strip()
        self._registry[canonical] = indicator_cls

        if aliases:
            for alias in aliases:
                self._aliases[alias.upper().strip()] = canonical

    def register_decorator(
        self, name: str, aliases: Optional[list[str]] = None
    ) -> Callable[[Type[Indicator]], Type[Indicator]]:
        """Decorator to register an indicator class."""
        def decorator(cls: Type[Indicator]) -> Type[Indicator]:
            self.register(name, cls, aliases=aliases)
            return cls
        return decorator

    def get_class(self, name: str) -> Type[Indicator]:
        """Look up the indicator class by name or alias."""
        key = name.upper().strip()
        if key in self._aliases:
            key = self._aliases[key]
        if key not in self._registry:
            raise KeyError(
                f"Indicator '{name}' not found in registry. "
                f"Available: {sorted(list(self._registry.keys()) + list(self._aliases.keys()))}"
            )
        return self._registry[key]

    def get(self, name: str, **kwargs: Any) -> Indicator:
        """
        Instantiate an indicator by name with provided parameters.

        Example:
            ind = registry.get("RSI", period=14)
            ind = registry.get("EMA", period=20)
        """
        cls = self.get_class(name)
        return cls(**kwargs)

    def list_indicators(self) -> dict[str, dict[str, Any]]:
        """
        Return metadata and descriptions for all registered indicators.
        """
        result = {}
        for canonical, cls in sorted(self._registry.items()):
            # Instantiate with defaults if possible to inspect metadata
            try:
                instance = cls()
                meta = instance.metadata
                result[canonical] = {
                    "name": meta.name,
                    "version": meta.version,
                    "description": meta.description,
                    "category": meta.category,
                    "parameters": meta.parameters,
                    "required_input_columns": list(meta.required_input_columns),
                    "output_columns": list(meta.output_columns),
                    "warmup_period": meta.warmup_period,
                    "class": f"{cls.__module__}.{cls.__name__}",
                }
            except Exception:
                # Fallback if no-arg __init__ is not supported
                result[canonical] = {
                    "name": canonical,
                    "version": "1.0.0",
                    "description": cls.__doc__.strip().split("\n")[0] if cls.__doc__ else "",
                    "category": "custom",
                    "parameters": {},
                    "class": f"{cls.__module__}.{cls.__name__}",
                }
        return result

    def is_registered(self, name: str) -> bool:
        """Check if an indicator name or alias is registered."""
        key = name.upper().strip()
        return key in self._registry or key in self._aliases


# Global singleton registry instance
default_registry = IndicatorRegistry()


def register_default_indicators(reg: IndicatorRegistry) -> None:
    """Populate registry with standard quantitative indicators."""
    from indicators.trend import SMA, EMA, WMA, HMA, ADX, Supertrend
    from indicators.momentum import RSI, StochasticOscillator, StochasticRSI, MACD, ROC
    from indicators.volatility import ATR, BollingerBands, BollingerBandWidth, HistoricalVolatility
    from indicators.volume import OBV, VolumeSMA, VolumeRatio, SessionVWAP, CVDProxy
    from indicators.price import (
        Returns,
        LogReturns,
        HighLowRange,
        TrueRange,
        PercentageChange,
        RollingHigh,
        RollingLow,
    )
    from indicators.session import SessionFeatures
    from indicators.ichimoku import IchimokuCloud

    # Trend
    reg.register("SMA", SMA)
    reg.register("EMA", EMA)
    reg.register("WMA", WMA)
    reg.register("HMA", HMA)
    reg.register("ADX", ADX)
    reg.register("SUPERTREND", Supertrend, aliases=["ST"])

    # Momentum
    reg.register("RSI", RSI)
    reg.register("STOCH", StochasticOscillator, aliases=["STOCHASTIC"])
    reg.register("STOCHRSI", StochasticRSI, aliases=["STOCH_RSI"])
    reg.register("MACD", MACD)
    reg.register("ROC", ROC)

    # Volatility
    reg.register("ATR", ATR)
    reg.register("BOLLINGERBANDS", BollingerBands, aliases=["BB", "BOLLINGER"])
    reg.register("BOLLINGERBANDWIDTH", BollingerBandWidth, aliases=["BBWIDTH", "BB_WIDTH"])
    reg.register("HISTORICALVOLATILITY", HistoricalVolatility, aliases=["HV", "HIST_VOL"])

    # Volume
    reg.register("OBV", OBV)
    reg.register("VOLUMESMA", VolumeSMA, aliases=["VOL_SMA"])
    reg.register("VOLUMERATIO", VolumeRatio, aliases=["VOL_RATIO"])
    reg.register("VWAP", SessionVWAP, aliases=["SESSION_VWAP"])
    reg.register("CVD", CVDProxy, aliases=["CVD_PROXY"])

    # Price
    reg.register("RETURNS", Returns)
    reg.register("LOGRETURNS", LogReturns, aliases=["LOG_RETURNS"])
    reg.register("HIGHLOWRANGE", HighLowRange, aliases=["HL_RANGE"])
    reg.register("TRUERANGE", TrueRange, aliases=["TR"])
    reg.register("PERCENTAGECHANGE", PercentageChange, aliases=["PCT_CHANGE"])
    reg.register("ROLLINGHIGH", RollingHigh, aliases=["ROLL_HIGH"])
    reg.register("ROLLINGLOW", RollingLow, aliases=["ROLL_LOW"])

    # Session & Ichimoku
    reg.register("SESSION", SessionFeatures, aliases=["SESSION_FEATURES"])
    reg.register("ICHIMOKU", IchimokuCloud, aliases=["ICHIMOKU_CLOUD"])


# Initialize default registry
register_default_indicators(default_registry)
