"""
Provider adapter registry and factory.

Decouples downstream consumers (backtest engines, execution managers, UI)
from concrete data providers. New broker/exchange providers can be added
dynamically at runtime without touching downstream consumer code.
"""

from __future__ import annotations

from typing import Callable, Optional

from data.interfaces import HistoricalDataProvider, LiveMarketDataProvider, MarketDataProvider
from data.providers.synthetic_provider import SyntheticHistoricalProvider
from data.providers.simulated_live_provider import SimulatedLiveMarketDataProvider


class DataProviderRegistry:
    """
    Central registry for data provider adapters.
    """

    _historical_factories: dict[str, Callable[[], HistoricalDataProvider]] = {}
    _live_factories: dict[str, Callable[[], LiveMarketDataProvider]] = {}

    @classmethod
    def register_historical_provider(
        cls,
        name: str,
        factory: Callable[[], HistoricalDataProvider],
    ) -> None:
        """Register a historical data provider factory."""
        cls._historical_factories[name.lower()] = factory

    @classmethod
    def register_live_provider(
        cls,
        name: str,
        factory: Callable[[], LiveMarketDataProvider],
    ) -> None:
        """Register a live data provider factory."""
        cls._live_factories[name.lower()] = factory

    @classmethod
    def get_historical_provider(cls, name: str = "synthetic") -> HistoricalDataProvider:
        """Instantiate a registered historical data provider by name."""
        key = name.lower()
        if key not in cls._historical_factories:
            raise KeyError(
                f"Historical data provider '{name}' not found. "
                f"Available providers: {list(cls._historical_factories.keys())}"
            )
        return cls._historical_factories[key]()

    @classmethod
    def get_live_provider(cls, name: str = "simulated") -> LiveMarketDataProvider:
        """Instantiate a registered live data provider by name."""
        key = name.lower()
        if key not in cls._live_factories:
            raise KeyError(
                f"Live data provider '{name}' not found. "
                f"Available providers: {list(cls._live_factories.keys())}"
            )
        return cls._live_factories[key]()

    @classmethod
    def list_historical_providers(cls) -> list[str]:
        return sorted(cls._historical_factories.keys())

    @classmethod
    def list_live_providers(cls) -> list[str]:
        return sorted(cls._live_factories.keys())


# Register defaults
DataProviderRegistry.register_historical_provider("synthetic", lambda: SyntheticHistoricalProvider())
DataProviderRegistry.register_live_provider("simulated", lambda: SimulatedLiveMarketDataProvider())
