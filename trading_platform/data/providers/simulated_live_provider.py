"""
Simulated live market data provider adapter.

Provides an offline, deterministic implementation of LiveMarketDataProvider.
Allows subscribing, receiving simulated ticks/quotes/snapshots, and publishing
events through the platform's EventBus.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.enums import EventType
from core.events import BarEvent, EventBus, QuoteEvent, TickEvent
from core.models import Asset, MarketDataSnapshot, OHLCVBar, Quote, Tick
from data.interfaces import LiveMarketDataProvider


class SimulatedLiveMarketDataProvider(LiveMarketDataProvider):
    """
    Offline/simulated implementation of LiveMarketDataProvider.
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self.event_bus = event_bus
        self._connected = False
        self._subscriptions: set[str] = set()
        self._latest_quotes: dict[str, Quote] = {}
        self._latest_ticks: dict[str, Tick] = {}
        self._latest_bars: dict[str, OHLCVBar] = {}

    def get_name(self) -> str:
        return "SimulatedLiveMarketDataProvider"

    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def subscribe(self, assets: list[Asset]) -> None:
        if not self._connected:
            self.connect()
        for a in assets:
            self._subscriptions.add(f"{a.symbol}@{a.exchange.value}")

    def unsubscribe(self, assets: list[Asset]) -> None:
        for a in assets:
            self._subscriptions.discard(f"{a.symbol}@{a.exchange.value}")

    def is_subscribed(self, asset: Asset) -> bool:
        return f"{asset.symbol}@{asset.exchange.value}" in self._subscriptions

    def emit_quote(self, quote: Quote) -> None:
        """Inject a quote and broadcast if subscribed."""
        key = f"{quote.asset.symbol}@{quote.asset.exchange.value}"
        self._latest_quotes[key] = quote
        if self.event_bus:
            self.event_bus.publish(
                QuoteEvent(
                    source=self.get_name(),
                    quote=quote,
                )
            )

    def emit_tick(self, tick: Tick) -> None:
        """Inject a tick and broadcast if subscribed."""
        key = f"{tick.asset.symbol}@{tick.asset.exchange.value}"
        self._latest_ticks[key] = tick
        if self.event_bus:
            self.event_bus.publish(
                TickEvent(
                    source=self.get_name(),
                    tick=tick,
                )
            )

    def emit_bar(self, bar: OHLCVBar) -> None:
        """Inject a completed bar and broadcast."""
        key = f"{bar.asset.symbol}@{bar.asset.exchange.value}"
        self._latest_bars[key] = bar
        if self.event_bus:
            self.event_bus.publish(
                BarEvent(
                    source=self.get_name(),
                    bar=bar,
                )
            )

    def get_quote(self, asset: Asset) -> Optional[Quote]:
        key = f"{asset.symbol}@{asset.exchange.value}"
        return self._latest_quotes.get(key)

    def get_snapshot(self, asset: Asset) -> Optional[MarketDataSnapshot]:
        key = f"{asset.symbol}@{asset.exchange.value}"
        tick = self._latest_ticks.get(key)
        quote = self._latest_quotes.get(key)
        bar = self._latest_bars.get(key)

        if not tick and not quote and not bar:
            return None

        # Build composite snapshot
        now = datetime.now(tz=timezone.utc)
        return MarketDataSnapshot(
            asset=asset,
            timestamp=now,
            last_tick=tick,
            best_quote=quote,
            last_bar=bar,
        )
