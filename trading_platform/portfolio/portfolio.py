"""
Portfolio Manager.

Maintains the real-time state of all positions, fills, and P&L.
Acts as the in-memory source-of-truth for portfolio state during
both live trading and backtesting.

The Portfolio is updated by the execution layer when fills arrive
and exposes a consistent view to analytics and risk modules.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.enums import PositionSide, Side
from core.models import (
    Account,
    Balance,
    Fill,
    Order,
    PortfolioSnapshot,
    Position,
    Trade,
)

logger = logging.getLogger(__name__)


class Portfolio:
    """
    In-memory portfolio state manager.

    Thread-safety: Not thread-safe in Phase 1. For concurrent
    live trading scenarios, wrap with locking or use an async-native design.
    """

    def __init__(self, account: Account) -> None:
        """
        Args:
            account: The brokerage account associated with this portfolio.
        """
        self._account = account
        self._positions: dict[str, Position] = {}  # key = asset symbol
        self._open_orders: dict[str, Order] = {}
        self._fill_history: list[Fill] = []
        self._trade_history: list[Trade] = []

        logger.info(
            "Portfolio initialized: account_id=%s broker=%s is_live=%s",
            account.account_id,
            account.broker_name,
            account.is_live,
        )

    # ──────────────────────────────────────────────
    # Fill processing
    # ──────────────────────────────────────────────

    def process_fill(self, fill: Fill, order: Order) -> None:
        """
        Apply a fill to the portfolio, updating the relevant position.

        Args:
            fill:  The execution fill from the broker.
            order: The original order that generated the fill.
        """
        self._fill_history.append(fill)
        symbol = fill.asset.symbol

        # Initialise position if it doesn't exist
        if symbol not in self._positions:
            self._positions[symbol] = Position(
                asset=fill.asset,
                side=PositionSide.FLAT,
                quantity=Decimal("0"),
                average_entry_price=Decimal("0"),
            )

        position = self._positions[symbol]

        if fill.side == Side.BUY:
            self._apply_buy_fill(position, fill)
        else:
            self._apply_sell_fill(position, fill, order)

        logger.info(
            "Portfolio.process_fill: symbol=%s side=%s qty=%s price=%s "
            "position_qty=%s avg_entry=%s",
            symbol,
            fill.side.value,
            fill.quantity,
            fill.price,
            position.quantity,
            position.average_entry_price,
        )

    def _apply_buy_fill(self, position: Position, fill: Fill) -> None:
        """Update a position with a buy fill (opening long or closing short)."""
        if position.side == PositionSide.FLAT or position.side == PositionSide.LONG:
            # Adding to / opening a long
            total_cost = (position.average_entry_price * position.quantity) + (
                fill.price * fill.quantity
            )
            position.quantity += fill.quantity
            if position.quantity > Decimal("0"):
                position.average_entry_price = total_cost / position.quantity
            position.side = PositionSide.LONG
        else:
            # Closing a short
            realized = (position.average_entry_price - fill.price) * fill.quantity
            position.realized_pnl += realized
            position.quantity -= fill.quantity
            if position.quantity <= Decimal("0"):
                position.side = PositionSide.FLAT
                position.quantity = Decimal("0")
                position.average_entry_price = Decimal("0")

    def _apply_sell_fill(
        self, position: Position, fill: Fill, order: Order
    ) -> None:
        """Update a position with a sell fill (closing long or opening short)."""
        if position.side == PositionSide.FLAT or position.side == PositionSide.SHORT:
            # Adding to / opening a short
            total_cost = (position.average_entry_price * position.quantity) + (
                fill.price * fill.quantity
            )
            position.quantity += fill.quantity
            if position.quantity > Decimal("0"):
                position.average_entry_price = total_cost / position.quantity
            position.side = PositionSide.SHORT
        else:
            # Closing a long
            realized = (fill.price - position.average_entry_price) * fill.quantity
            position.realized_pnl += realized
            position.quantity -= fill.quantity
            if position.quantity <= Decimal("0"):
                position.side = PositionSide.FLAT
                position.quantity = Decimal("0")
                position.average_entry_price = Decimal("0")

    # ──────────────────────────────────────────────
    # Mark-to-market
    # ──────────────────────────────────────────────

    def mark_to_market(self, symbol: str, current_price: Decimal) -> None:
        """
        Update the unrealized P&L for a specific position.

        Args:
            symbol:        The instrument symbol.
            current_price: The latest market price.
        """
        if symbol in self._positions:
            self._positions[symbol].mark_to_market(current_price)

    # ──────────────────────────────────────────────
    # Queries
    # ──────────────────────────────────────────────

    def get_position(self, symbol: str) -> Optional[Position]:
        """Return the position for a given symbol, or None if flat."""
        return self._positions.get(symbol)

    def get_open_positions(self) -> list[Position]:
        """Return all positions with non-zero quantity."""
        return [
            p for p in self._positions.values() if p.quantity > Decimal("0")
        ]

    def get_total_unrealized_pnl(self) -> Decimal:
        return sum(
            (p.unrealized_pnl for p in self._positions.values()), Decimal("0")
        )

    def get_total_realized_pnl(self) -> Decimal:
        return sum(
            (p.realized_pnl for p in self._positions.values()), Decimal("0")
        )

    def snapshot(self, timestamp: Optional[datetime] = None) -> PortfolioSnapshot:
        """
        Generate a point-in-time immutable portfolio snapshot.

        Args:
            timestamp: Snapshot time (defaults to current UTC).

        Returns:
            PortfolioSnapshot instance.
        """
        ts = timestamp or datetime.now(tz=timezone.utc)
        balance = self._account.get_balance()
        cash = balance.available if balance else Decimal("0")
        total_equity = balance.total_equity if balance else Decimal("0")

        return PortfolioSnapshot(
            timestamp=ts,
            account_id=self._account.account_id,
            positions=list(self._positions.values()),
            total_equity=total_equity,
            total_unrealized_pnl=self.get_total_unrealized_pnl(),
            total_realized_pnl=self.get_total_realized_pnl(),
            cash_balance=cash,
        )

    @property
    def account(self) -> Account:
        return self._account

    @property
    def fill_history(self) -> list[Fill]:
        return list(self._fill_history)

    @property
    def trade_history(self) -> list[Trade]:
        return list(self._trade_history)
