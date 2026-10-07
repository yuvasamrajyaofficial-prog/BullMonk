"""
Domain event bus and event definitions.

The event-driven architecture decouples producers (data providers, strategies)
from consumers (risk manager, portfolio, analytics) without direct references.

Events flow through a synchronous in-process bus for Phase 1.
An async / message-queue backed bus can replace this at Phase 2
without changing any subscriber code.
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from pydantic import BaseModel, Field

from core.enums import EventType

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ──────────────────────────────────────────────
# Base Event
# ──────────────────────────────────────────────

class Event(BaseModel):
    """Base class for all platform events."""

    model_config = {"frozen": True}

    event_id: str = Field(default_factory=_new_uuid)
    event_type: EventType
    timestamp: datetime = Field(default_factory=_utc_now)
    source: Optional[str] = Field(
        default=None, description="Identifier of the component that emitted this event"
    )
    payload: dict[str, Any] = Field(
        default_factory=dict, description="Event-specific data payload"
    )


# ──────────────────────────────────────────────
# Typed Event Subclasses
# ──────────────────────────────────────────────

class MarketDataEvent(Event):
    """Emitted when new market data (bar, tick, quote) is available."""
    event_type: EventType = EventType.MARKET_DATA


class BarEvent(Event):
    """Emitted when a new OHLCV bar is completed."""
    event_type: EventType = EventType.BAR


class TickEvent(Event):
    """Emitted on each new trade tick."""
    event_type: EventType = EventType.TICK


class QuoteEvent(Event):
    """Emitted on each new best bid/ask quote update."""
    event_type: EventType = EventType.QUOTE


class SignalEvent(Event):
    """Emitted when a strategy generates a trading signal."""
    event_type: EventType = EventType.SIGNAL


class OrderRequestEvent(Event):
    """Emitted by a strategy when it wants to place an order."""
    event_type: EventType = EventType.ORDER_REQUEST


class OrderSubmittedEvent(Event):
    """Emitted when an order has been submitted to the broker."""
    event_type: EventType = EventType.ORDER_SUBMITTED


class OrderFilledEvent(Event):
    """Emitted when an order fill confirmation is received."""
    event_type: EventType = EventType.ORDER_FILLED


class OrderCancelledEvent(Event):
    """Emitted when an order is cancelled."""
    event_type: EventType = EventType.ORDER_CANCELLED


class OrderRejectedEvent(Event):
    """Emitted when an order is rejected by the broker or risk engine."""
    event_type: EventType = EventType.ORDER_REJECTED


class PositionUpdatedEvent(Event):
    """Emitted when a position is created, modified, or closed."""
    event_type: EventType = EventType.POSITION_UPDATED


class RiskBreachEvent(Event):
    """Emitted when the risk manager detects a limit breach."""
    event_type: EventType = EventType.RISK_BREACH


class StrategyStartEvent(Event):
    """Emitted when a strategy starts."""
    event_type: EventType = EventType.STRATEGY_START


class StrategyStopEvent(Event):
    """Emitted when a strategy stops."""
    event_type: EventType = EventType.STRATEGY_STOP


class HeartbeatEvent(Event):
    """Periodic liveness heartbeat."""
    event_type: EventType = EventType.HEARTBEAT


class ErrorEvent(Event):
    """Emitted when an unrecoverable error occurs in a component."""
    event_type: EventType = EventType.ERROR


# ──────────────────────────────────────────────
# Event Handler Type
# ──────────────────────────────────────────────

EventHandler = Callable[[Event], None]


# ──────────────────────────────────────────────
# Event Bus
# ──────────────────────────────────────────────

class EventBus:
    """
    Synchronous, in-process publish/subscribe event bus.

    Subscribers register handlers for specific EventTypes.
    When an event is published, all registered handlers for that
    event type are called in registration order.

    Thread-safety: Not thread-safe in Phase 1. For concurrent
    live trading, replace with an asyncio-based or queue-backed bus.
    """

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[EventHandler]] = defaultdict(list)
        self._wildcard_handlers: list[EventHandler] = []

    def subscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: The event type to listen for.
            handler: Callable that accepts a single Event argument.
        """
        self._handlers[event_type].append(handler)
        logger.debug(
            "EventBus.subscribe: handler=%s registered for event_type=%s",
            getattr(handler, "__qualname__", repr(handler)),
            event_type.value,
        )

    def subscribe_all(self, handler: EventHandler) -> None:
        """
        Register a handler that receives ALL event types.

        Args:
            handler: Callable that accepts a single Event argument.
        """
        self._wildcard_handlers.append(handler)
        logger.debug(
            "EventBus.subscribe_all: wildcard handler=%s registered",
            getattr(handler, "__qualname__", repr(handler)),
        )

    def unsubscribe(self, event_type: EventType, handler: EventHandler) -> None:
        """
        Remove a previously registered handler.

        Args:
            event_type: The event type the handler was registered for.
            handler: The exact handler callable to remove.
        """
        try:
            self._handlers[event_type].remove(handler)
        except ValueError:
            logger.warning(
                "EventBus.unsubscribe: handler=%s not found for event_type=%s",
                getattr(handler, "__qualname__", repr(handler)),
                event_type.value,
            )

    def publish(self, event: Event) -> None:
        """
        Publish an event to all registered subscribers.

        Errors in handlers are caught and logged but do NOT
        halt delivery to remaining handlers (fail-fast per handler,
        not per publish call).

        Args:
            event: The event to publish.
        """
        logger.debug(
            "EventBus.publish: event_type=%s event_id=%s source=%s",
            event.event_type.value,
            event.event_id,
            event.source,
        )

        all_handlers = (
            self._handlers.get(event.event_type, []) + self._wildcard_handlers
        )

        for handler in all_handlers:
            try:
                handler(event)
            except Exception:
                logger.exception(
                    "EventBus: unhandled exception in handler=%s for event_type=%s event_id=%s",
                    getattr(handler, "__qualname__", repr(handler)),
                    event.event_type.value,
                    event.event_id,
                )

    def subscriber_count(self, event_type: EventType) -> int:
        """Return the number of handlers registered for a given event type."""
        return len(self._handlers.get(event_type, []))

    def clear(self) -> None:
        """Remove all subscribers. Useful for test teardown."""
        self._handlers.clear()
        self._wildcard_handlers.clear()
