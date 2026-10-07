"""
Abstract Strategy interface.

The Strategy contract is the boundary between trading logic and
execution infrastructure. A Strategy:

- Receives market data events.
- Emits Signal objects (NOT orders directly).
- Has no knowledge of which broker is being used.
- Has no knowledge of whether it is running in backtest or live mode.

Concrete strategies extend BaseStrategy and implement on_bar() and/or on_tick().

Lifecycle:
  initialize() → on_bar()/on_tick() [N times] → on_stop()
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Optional

from core.clock import Clock
from core.enums import StrategyState
from core.events import EventBus
from core.models import (
    OHLCVBar,
    Quote,
    Signal,
    StrategyConfig,
    StrategyMetadata,
    Tick,
)

logger = logging.getLogger(__name__)


class BaseStrategy(ABC):
    """
    Abstract base class for all trading strategies.

    Strategies are NOT allowed to:
    - Import or reference any broker implementation or broker SDKs.
    - Place orders directly — they emit Signals only.
    - Access the file system or network directly.
    - Use wall-clock time — they must use the injected Clock.

    Strategies ARE allowed to:
    - Maintain internal state (indicators, position tracking, etc.)
    - Emit multiple Signals per bar.
    - Access the EventBus to publish events.
    """

    def __init__(
        self,
        config: StrategyConfig,
        clock: Clock,
        event_bus: EventBus,
    ) -> None:
        """
        Args:
            config:    Strategy runtime parameters.
            clock:     Injected clock (live or simulated).
            event_bus: Event bus for publishing signals/events.
        """
        self._config = config
        self._clock = clock
        self._event_bus = event_bus
        self._state: StrategyState = StrategyState.INITIALIZED
        self._signals_emitted: int = 0

    # ──────────────────────────────────────────────
    # Metadata (subclasses must override)
    # ──────────────────────────────────────────────

    @property
    @abstractmethod
    def metadata(self) -> StrategyMetadata:
        """Static description of this strategy."""

    # ──────────────────────────────────────────────
    # Lifecycle hooks
    # ──────────────────────────────────────────────

    def initialize(self) -> None:
        """
        Called once before the first market data event.

        Subclasses should load any required resources, warm-up
        indicator buffers, or set initial state here.
        Override this method; call super().initialize() first.
        """
        self._state = StrategyState.RUNNING
        logger.info(
            "Strategy initialized: id=%s name=%s",
            self._config.strategy_id,
            self.metadata.name,
        )

    def on_stop(self) -> None:
        """
        Called when the strategy is being stopped.

        Subclasses should clean up resources and close any open positions
        if required by the strategy logic. Override and call super().on_stop().
        """
        self._state = StrategyState.STOPPED
        logger.info(
            "Strategy stopped: id=%s total_signals_emitted=%d",
            self._config.strategy_id,
            self._signals_emitted,
        )

    # ──────────────────────────────────────────────
    # Market data hooks (subclasses override as needed)
    # ──────────────────────────────────────────────

    def on_bar(self, bar: OHLCVBar) -> Optional[list[Signal]]:
        """
        Called on each completed OHLCV bar.

        Args:
            bar: The newly completed bar.

        Returns:
            A list of Signal objects, or None / empty list if no signal.
        """
        return None

    def on_tick(self, tick: Tick) -> Optional[list[Signal]]:
        """
        Called on each trade tick.

        Args:
            tick: The latest trade tick.

        Returns:
            A list of Signal objects, or None / empty list if no signal.
        """
        return None

    def on_quote(self, quote: Quote) -> Optional[list[Signal]]:
        """
        Called on each best bid/ask quote update.

        Args:
            quote: The latest quote.

        Returns:
            A list of Signal objects, or None / empty list if no signal.
        """
        return None

    # ──────────────────────────────────────────────
    # Protected helpers
    # ──────────────────────────────────────────────

    def _emit_signal(self, signal: Signal) -> None:
        """
        Publish a signal to the event bus.

        Args:
            signal: The trading signal to emit.
        """
        from core.events import SignalEvent

        self._signals_emitted += 1
        logger.debug(
            "Strategy signal: strategy_id=%s signal_type=%s asset=%s",
            signal.strategy_id,
            signal.signal_type.value,
            signal.asset,
        )
        self._event_bus.publish(
            SignalEvent(
                source=self._config.strategy_id,
                payload={"signal": signal.model_dump()},
            )
        )

    # ──────────────────────────────────────────────
    # Properties
    # ──────────────────────────────────────────────

    @property
    def strategy_id(self) -> str:
        return self._config.strategy_id

    @property
    def state(self) -> StrategyState:
        return self._state

    @property
    def config(self) -> StrategyConfig:
        return self._config

    @property
    def signals_emitted(self) -> int:
        return self._signals_emitted
