"""
Abstract Broker interface.

The Broker interface exposes generic brokerage operations.
Concrete implementations (DhanBroker, ZerodhaBroker, BinanceBroker, etc.)
live in brokers/<name>/ subdirectories and are loaded via dependency injection.

No strategy code may import from this module's implementations.
Only the abstract BaseBroker is visible to strategy/execution infrastructure.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.models import Account, Asset, Fill, Order, Position, Quote
from core.enums import Side, OrderType, TimeInForce, ProductType
from decimal import Decimal


class BaseBroker(ABC):
    """
    Abstract broker interface.

    All broker adapters must implement this interface.
    The interface is intentionally generic — it must work for
    Indian equity, F&O, Forex, and Crypto without modification.
    """

    @abstractmethod
    def get_name(self) -> str:
        """Return the human-readable name of this broker (e.g. 'Dhan', 'Zerodha')."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Return True if the broker session is active and authenticated."""

    @abstractmethod
    def connect(self) -> None:
        """
        Establish a session with the broker API.

        Raises:
            BrokerConnectionError:      If connection fails.
            BrokerAuthenticationError:  If credentials are invalid.
        """

    @abstractmethod
    def disconnect(self) -> None:
        """Gracefully terminate the broker session."""

    # ──────────────────────────────────────────────
    # Account
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_account(self) -> Account:
        """
        Fetch the current account details and balances.

        Returns:
            Account object with current balance information.

        Raises:
            BrokerError: On API failure.
        """

    # ──────────────────────────────────────────────
    # Positions
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_positions(self) -> list[Position]:
        """
        Fetch all currently open positions.

        Returns:
            List of Position objects (empty if flat).

        Raises:
            BrokerError: On API failure.
        """

    # ──────────────────────────────────────────────
    # Orders
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_orders(self, status_filter: Optional[list[str]] = None) -> list[Order]:
        """
        Fetch orders, optionally filtered by status.

        Args:
            status_filter: Optional list of OrderStatus strings to filter by.

        Returns:
            List of Order objects.

        Raises:
            BrokerError: On API failure.
        """

    @abstractmethod
    def get_order(self, order_id: str) -> Order:
        """
        Fetch a single order by platform order ID.

        Args:
            order_id: The platform-assigned order ID.

        Returns:
            The Order object.

        Raises:
            OrderNotFoundError: If the order does not exist.
            BrokerError:        On API failure.
        """

    @abstractmethod
    def place_order(self, order: Order) -> str:
        """
        Submit an order to the broker.

        Args:
            order: The fully constructed Order to place.
                   The broker implementation must translate this to
                   broker-specific parameters internally.

        Returns:
            The broker-assigned order ID string.

        Raises:
            OrderValidationError: If the order fails broker-side validation.
            OrderRejectedError:   If the exchange rejects the order.
            BrokerError:          On API failure.
        """

    @abstractmethod
    def cancel_order(self, order_id: str) -> None:
        """
        Request cancellation of an open order.

        Args:
            order_id: The platform order ID to cancel.

        Raises:
            OrderNotFoundError:    If the order does not exist.
            OrderCancellationError: If cancellation fails.
            BrokerError:           On API failure.
        """

    @abstractmethod
    def modify_order(
        self,
        order_id: str,
        *,
        quantity: Optional[Decimal] = None,
        limit_price: Optional[Decimal] = None,
        stop_price: Optional[Decimal] = None,
    ) -> None:
        """
        Modify an open order's quantity or price.

        Args:
            order_id:    The platform order ID to modify.
            quantity:    New total quantity (optional).
            limit_price: New limit price (optional).
            stop_price:  New stop price (optional).

        Raises:
            OrderNotFoundError:    If the order does not exist.
            OrderModificationError: If modification fails.
            BrokerError:           On API failure.
        """

    # ──────────────────────────────────────────────
    # Market data (lightweight — for live price checks)
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_quote(self, asset: Asset) -> Quote:
        """
        Fetch the current best bid/ask quote for an instrument.

        Args:
            asset: The instrument to query.

        Returns:
            Current Quote object.

        Raises:
            DataProviderError: If the quote cannot be retrieved.
            BrokerError:       On API failure.
        """

    # ──────────────────────────────────────────────
    # Fill history
    # ──────────────────────────────────────────────

    @abstractmethod
    def get_fills(self, order_id: Optional[str] = None) -> list[Fill]:
        """
        Fetch trade fill records.

        Args:
            order_id: If provided, return fills for a specific order only.

        Returns:
            List of Fill objects.

        Raises:
            BrokerError: On API failure.
        """
