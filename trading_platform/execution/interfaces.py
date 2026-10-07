"""
Execution layer interfaces.

These define the contract between the strategy signal layer
and the order routing / broker connectivity layer.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.models import Fill, Order, Signal
from core.enums import OrderStatus


class OrderExecutor(ABC):
    """
    Abstract interface for order routing and execution.

    Receives signals (from strategies) and translates them into
    orders that are then submitted to a broker. The executor
    applies sizing, routing logic, and pre-submission validation.
    """

    @abstractmethod
    def execute_signal(self, signal: Signal) -> Optional[Order]:
        """
        Translate a trading signal into an order and submit it.

        Args:
            signal: The signal emitted by a strategy.

        Returns:
            The created Order if submission succeeded, else None.

        Raises:
            OrderValidationError: If the translated order is invalid.
            RiskError:            If the risk manager vetoes the order.
        """

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """
        Cancel an open order.

        Args:
            order_id: Platform order ID to cancel.

        Raises:
            OrderNotFoundError:    If the order does not exist.
            OrderCancellationError: If cancellation fails.
        """

    @abstractmethod
    def get_open_orders(self) -> list[Order]:
        """Return all orders that are currently open / active."""

    @abstractmethod
    def get_order_history(self) -> list[Order]:
        """Return all historical orders (including terminal states)."""


class PortfolioRepository(ABC):
    """
    Abstract interface for persisting and retrieving portfolio state.

    Implementations may use an in-memory store (backtesting),
    a relational database, or Redis (live trading).
    """

    @abstractmethod
    def save_order(self, order: Order) -> None:
        """Persist or update an order record."""

    @abstractmethod
    def get_order(self, order_id: str) -> Optional[Order]:
        """Retrieve an order by its platform ID."""

    @abstractmethod
    def save_fill(self, fill: Fill) -> None:
        """Persist a fill record."""

    @abstractmethod
    def get_fills_for_order(self, order_id: str) -> list[Fill]:
        """Retrieve all fills associated with a given order."""

    @abstractmethod
    def save_position(self, position: "Position") -> None:  # type: ignore[name-defined]
        """Persist or update a position record."""

    @abstractmethod
    def get_position(self, symbol: str, exchange: str) -> Optional["Position"]:  # type: ignore[name-defined]
        """Retrieve an open position by symbol and exchange."""

    @abstractmethod
    def get_all_positions(self) -> list["Position"]:  # type: ignore[name-defined]
        """Retrieve all open positions."""
