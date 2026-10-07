"""
Abstract interfaces and protocols for data providers.

These define the contract that all market data sources must fulfil.
Concrete implementations (Dhan, Zerodha, CSV, database, etc.)
live in their own adapter modules and must NOT bleed into this file.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import AsyncIterator, Iterator, Optional

from core.models import Asset, MarketDataSnapshot, OHLCVBar, Quote, Tick
from core.enums import Timeframe


class MarketDataProvider(ABC):
    """Root abstract base for all market data sources."""

    @abstractmethod
    def get_name(self) -> str:
        """Human-readable name of this data provider (e.g. 'DhanHistorical')."""


class HistoricalDataProvider(MarketDataProvider):
    """
    Interface for providers of historical OHLCV data.

    Implementations must return data in ascending chronological order.
    All timestamps must be UTC timezone-aware.
    """

    @abstractmethod
    def get_bars(
        self,
        asset: Asset,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
        *,
        limit: Optional[int] = None,
    ) -> list[OHLCVBar]:
        """
        Fetch historical OHLCV bars.

        Args:
            asset:     The instrument to fetch data for.
            timeframe: Bar granularity (1m, 5m, 1d, etc.).
            start:     Inclusive start datetime (UTC, timezone-aware).
            end:       Inclusive end datetime (UTC, timezone-aware).
            limit:     Optional maximum number of bars to return.

        Returns:
            List of OHLCVBar objects in ascending chronological order.

        Raises:
            DataProviderError:  On provider-level failure.
            DataNotFoundError:  If no data exists for the requested range.
        """

    @abstractmethod
    def get_latest_bar(
        self,
        asset: Asset,
        timeframe: Timeframe,
    ) -> Optional[OHLCVBar]:
        """
        Return the most recent completed bar.

        Returns:
            The latest OHLCVBar, or None if unavailable.
        """

    @abstractmethod
    def get_assets(self) -> list[Asset]:
        """Return all instruments available from this provider."""


class LiveMarketDataProvider(MarketDataProvider):
    """
    Interface for real-time / streaming market data providers.

    Implementations handle WebSocket or SSE connections and push
    data to the platform via the event bus.
    """

    @abstractmethod
    def subscribe(self, assets: list[Asset]) -> None:
        """
        Subscribe to real-time data for the given instruments.

        Args:
            assets: Instruments to subscribe to.

        Raises:
            DataProviderError: If subscription fails.
        """

    @abstractmethod
    def unsubscribe(self, assets: list[Asset]) -> None:
        """
        Unsubscribe from real-time data for the given instruments.

        Args:
            assets: Instruments to unsubscribe from.
        """

    @abstractmethod
    def get_quote(self, asset: Asset) -> Optional[Quote]:
        """
        Return the latest cached best bid/ask quote.

        Args:
            asset: The instrument to query.

        Returns:
            Latest Quote, or None if no data has arrived yet.
        """

    @abstractmethod
    def get_snapshot(self, asset: Asset) -> Optional[MarketDataSnapshot]:
        """
        Return a composite market snapshot (tick + quote + last bar).

        Args:
            asset: The instrument to query.

        Returns:
            MarketDataSnapshot or None.
        """

    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if the underlying connection is active."""

    @abstractmethod
    def connect(self) -> None:
        """Establish the connection to the data provider."""

    @abstractmethod
    def disconnect(self) -> None:
        """Gracefully close the connection."""
