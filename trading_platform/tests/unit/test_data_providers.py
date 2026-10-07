"""
Unit tests for data provider adapters and the DataProviderRegistry.

Tests:
1. SyntheticHistoricalProvider: get_bars, get_latest_bar, limit parameter.
2. CachedHistoricalDataProvider: cache hit returns cached bars, cache miss calls underlying.
3. SimulatedLiveMarketDataProvider: subscribe, unsubscribe, emit ticks/quotes/bars, EventBus integration.
4. DataProviderRegistry: registration and lookup of historical and live providers.
"""

from __future__ import annotations

import shutil
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from tempfile import mkdtemp

import pytest

from core.enums import EventType, Timeframe
from core.events import EventBus
from core.models import Quote, Tick
from data.cache import DataCache
from data.nifty import create_nifty_index
from data.providers import (
    CachedHistoricalDataProvider,
    DataProviderRegistry,
    SimulatedLiveMarketDataProvider,
    SyntheticHistoricalProvider,
)


@pytest.fixture
def temp_cache_dir():
    d = mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


class TestDataProviders:

    def test_synthetic_historical_provider_get_bars(self):
        provider = SyntheticHistoricalProvider(seed=42)
        asset = create_nifty_index()

        start = datetime(2025, 1, 6, 3, 45, tzinfo=timezone.utc)
        end = datetime(2025, 1, 6, 10, 0, tzinfo=timezone.utc)

        bars = provider.get_bars(asset, Timeframe.M5, start, end)
        assert len(bars) > 0
        assert bars[0].asset == asset
        assert bars[0].is_synthetic is True

        # Test limit parameter
        limited_bars = provider.get_bars(asset, Timeframe.M5, start, end, limit=10)
        assert len(limited_bars) == 10

    def test_cached_provider_transparent_caching(self, temp_cache_dir: Path):
        cache = DataCache(cache_dir=temp_cache_dir)
        synth = SyntheticHistoricalProvider(seed=42)
        cached_prov = CachedHistoricalDataProvider(underlying_provider=synth, cache=cache)
        asset = create_nifty_index()

        start = datetime(2025, 1, 6, 3, 45, tzinfo=timezone.utc)
        end = datetime(2025, 1, 6, 10, 0, tzinfo=timezone.utc)

        assert cache.exists(asset, Timeframe.M5) is False

        # First call fetches from underlying and caches
        bars1 = cached_prov.get_bars(asset, Timeframe.M5, start, end)
        assert len(bars1) > 0
        assert cache.exists(asset, Timeframe.M5) is True

        # Second call loads from cache
        bars2 = cached_prov.get_bars(asset, Timeframe.M5, start, end)
        assert len(bars2) == len(bars1)
        assert bars2[0].open == bars1[0].open

    def test_simulated_live_provider_subscription_and_events(self):
        bus = EventBus()
        live = SimulatedLiveMarketDataProvider(event_bus=bus)
        asset = create_nifty_index()

        # Subscribe
        live.subscribe([asset])
        assert live.is_connected() is True
        assert live.is_subscribed(asset) is True

        received_ticks = []
        bus.subscribe(EventType.TICK, received_ticks.append)

        # Emit tick
        now = datetime.now(tz=timezone.utc)
        test_tick = Tick(
            asset=asset,
            timestamp=now,
            last_price=Decimal("24050.25"),
            last_quantity=Decimal("150"),
        )
        live.emit_tick(test_tick)

        assert len(received_ticks) == 1
        assert received_ticks[0].tick.last_price == Decimal("24050.25")

        # Emit quote and check latest quote
        test_quote = Quote(
            asset=asset,
            timestamp=now,
            bid_price=Decimal("24050.00"),
            bid_size=Decimal("500"),
            ask_price=Decimal("24050.50"),
            ask_size=Decimal("600"),
        )
        live.emit_quote(test_quote)
        latest_q = live.get_quote(asset)
        assert latest_q is not None
        assert latest_q.bid_price == Decimal("24050.00")

        # Snapshot
        snapshot = live.get_snapshot(asset)
        assert snapshot is not None
        assert snapshot.last_tick is not None
        assert snapshot.last_tick.last_price == Decimal("24050.25")
        assert snapshot.best_quote is not None
        assert snapshot.best_quote.bid_price == Decimal("24050.00")

        # Unsubscribe
        live.unsubscribe([asset])
        assert live.is_subscribed(asset) is False

    def test_provider_registry(self):
        assert "synthetic" in DataProviderRegistry.list_historical_providers()
        assert "simulated" in DataProviderRegistry.list_live_providers()

        h_prov = DataProviderRegistry.get_historical_provider("synthetic")
        assert isinstance(h_prov, SyntheticHistoricalProvider)

        l_prov = DataProviderRegistry.get_live_provider("simulated")
        assert isinstance(l_prov, SimulatedLiveMarketDataProvider)

        # Custom provider registration
        class DummyProvider(SyntheticHistoricalProvider):
            def get_name(self) -> str:
                return "Dummy"

        DataProviderRegistry.register_historical_provider("dummy", lambda: DummyProvider())
        assert "dummy" in DataProviderRegistry.list_historical_providers()
        assert DataProviderRegistry.get_historical_provider("dummy").get_name() == "Dummy"
