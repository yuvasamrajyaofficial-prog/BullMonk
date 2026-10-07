"""
Unit tests for the EventBus.

Tests that:
1. Handlers receive published events.
2. Wildcard handlers receive all event types.
3. Errors in handlers don't stop delivery to other handlers.
4. Unsubscribe works correctly.
5. Subscriber count is accurate.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone

from core.enums import EventType
from core.events import (
    BarEvent,
    Event,
    EventBus,
    RiskBreachEvent,
    SignalEvent,
)


class TestEventBus:
    @pytest.fixture(autouse=True)
    def fresh_bus(self):
        self.bus = EventBus()

    def test_subscriber_receives_event(self):
        received = []
        self.bus.subscribe(EventType.BAR, received.append)
        event = BarEvent(source="test")
        self.bus.publish(event)
        assert len(received) == 1
        assert received[0].event_id == event.event_id

    def test_subscriber_does_not_receive_other_event_types(self):
        received = []
        self.bus.subscribe(EventType.BAR, received.append)
        self.bus.publish(RiskBreachEvent(source="test"))
        assert len(received) == 0

    def test_multiple_subscribers_for_same_type(self):
        r1, r2 = [], []
        self.bus.subscribe(EventType.SIGNAL, r1.append)
        self.bus.subscribe(EventType.SIGNAL, r2.append)
        self.bus.publish(SignalEvent(source="test"))
        assert len(r1) == 1
        assert len(r2) == 1

    def test_wildcard_handler_receives_all_types(self):
        received = []
        self.bus.subscribe_all(received.append)
        self.bus.publish(BarEvent(source="t"))
        self.bus.publish(SignalEvent(source="t"))
        self.bus.publish(RiskBreachEvent(source="t"))
        assert len(received) == 3

    def test_handler_error_does_not_stop_other_handlers(self):
        good_received = []

        def bad_handler(event):
            raise RuntimeError("Intentional error")

        self.bus.subscribe(EventType.BAR, bad_handler)
        self.bus.subscribe(EventType.BAR, good_received.append)

        # Should not raise — bad handler error is caught and logged
        self.bus.publish(BarEvent(source="test"))
        assert len(good_received) == 1

    def test_unsubscribe_removes_handler(self):
        received = []
        self.bus.subscribe(EventType.BAR, received.append)
        self.bus.unsubscribe(EventType.BAR, received.append)
        self.bus.publish(BarEvent(source="test"))
        assert len(received) == 0

    def test_subscriber_count(self):
        assert self.bus.subscriber_count(EventType.BAR) == 0
        self.bus.subscribe(EventType.BAR, lambda e: None)
        self.bus.subscribe(EventType.BAR, lambda e: None)
        assert self.bus.subscriber_count(EventType.BAR) == 2

    def test_clear_removes_all_handlers(self):
        received = []
        self.bus.subscribe(EventType.BAR, received.append)
        self.bus.subscribe_all(received.append)
        self.bus.clear()
        self.bus.publish(BarEvent(source="test"))
        assert len(received) == 0

    def test_event_has_unique_ids(self):
        ids = set()
        for _ in range(100):
            e = BarEvent(source="test")
            ids.add(e.event_id)
        assert len(ids) == 100

    def test_event_timestamp_is_utc_aware(self):
        event = SignalEvent(source="test")
        assert event.timestamp.tzinfo is not None
