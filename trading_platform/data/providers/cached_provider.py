"""
Cached historical data provider decorator.

Wraps any underlying HistoricalDataProvider with a DataCache layer:
1. Checks local cache first.
2. If hit and covers requested range, returns cached data directly.
3. If miss, queries underlying provider, caches the result, and returns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from core.enums import DataSource, Timeframe
from core.models import Asset, OHLCVBar
from data.cache import DataCache
from data.interfaces import HistoricalDataProvider


class CachedHistoricalDataProvider(HistoricalDataProvider):
    """
    Transparent caching proxy for any HistoricalDataProvider.
    """

    def __init__(
        self,
        underlying_provider: HistoricalDataProvider,
        cache: Optional[DataCache] = None,
        prefer_cached: bool = True,
    ) -> None:
        self.underlying = underlying_provider
        self.cache = cache or DataCache()
        self.prefer_cached = prefer_cached

    def get_name(self) -> str:
        return f"Cached[{self.underlying.get_name()}]"

    def get_assets(self) -> list[Asset]:
        return self.underlying.get_assets()

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
        Retrieve bars, using local cache when available.
        """
        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        # Check cache
        if self.prefer_cached and self.cache.exists(asset, timeframe):
            try:
                cached_bars = self.cache.load(asset, timeframe, start=start_utc, end=end_utc)
                if cached_bars and cached_bars[0].timestamp <= start_utc and cached_bars[-1].timestamp >= end_utc:
                    return cached_bars[-limit:] if limit else cached_bars
            except Exception:
                pass  # Fallback to fetching fresh

        # Fetch from underlying provider
        fresh_bars = self.underlying.get_bars(asset, timeframe, start_utc, end_utc, limit=limit)
        if fresh_bars:
            try:
                self.cache.save(asset, timeframe, fresh_bars)
            except Exception:
                pass

        return fresh_bars

    def get_latest_bar(
        self,
        asset: Asset,
        timeframe: Timeframe,
    ) -> Optional[OHLCVBar]:
        return self.underlying.get_latest_bar(asset, timeframe)
