"""
Simulated Order Matching Engine for Backtesting.

Enforces strict temporal causality and realistic exchange matching rules:
- Market orders executed at the next bar's Open (or current bar's Open/Close).
- Limit orders executed only if the bar range crosses the limit price.
- Stop orders triggered when the bar touches the stop price (accounting for gaps).
- Integration with SlippageModel and CostModel for accurate net fill prices and commissions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Optional
import uuid

from backtesting.costs import CostModel, IndianMarketCostModel, SlippageModel, ZeroSlippageModel
from core.enums import OrderStatus, OrderType, Side
from core.models import Fill, OHLCVBar, Order

logger = logging.getLogger(__name__)


@dataclass
class MatchResult:
    """Outcome of evaluating an order against a price bar."""

    order: Order
    fill: Optional[Fill] = None
    is_filled: bool = False
    is_cancelled: bool = False
    rejection_reason: Optional[str] = None


class SimulatedMatchingEngine:
    """
    Deterministic simulated order matching engine.
    
    Maintains an active order book of resting orders and evaluates
    them bar-by-bar against market prices.
    """

    def __init__(
        self,
        cost_model: Optional[CostModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        fill_on_next_open: bool = True,
    ) -> None:
        """
        Args:
            cost_model: Calculates statutory fees, STT, and brokerage.
            slippage_model: Calculates execution price slippage.
            fill_on_next_open: If True, market orders submitted on bar t fill at bar t+1 Open
                               to strictly prevent look-ahead bias.
        """
        self.cost_model = cost_model or IndianMarketCostModel()
        self.slippage_model = slippage_model or ZeroSlippageModel()
        self.fill_on_next_open = fill_on_next_open
        self._pending_orders: list[Order] = []
        self._active_limit_orders: list[Order] = []
        self._executed_fills: list[Fill] = []

    def submit_order(self, order: Order) -> None:
        """Queue an order into the matching engine."""
        if order.order_type == OrderType.MARKET:
            self._pending_orders.append(order)
        elif order.order_type in (OrderType.LIMIT, OrderType.STOP, OrderType.STOP_LIMIT):
            self._active_limit_orders.append(order)
        else:
            self._pending_orders.append(order)

    def cancel_order(self, order_id: str) -> bool:
        """Cancel an active resting order."""
        for i, order in enumerate(self._active_limit_orders):
            if order.order_id == order_id:
                self._active_limit_orders.pop(i)
                return True
        for i, order in enumerate(self._pending_orders):
            if order.order_id == order_id:
                self._pending_orders.pop(i)
                return True
        return False

    def process_bar(self, bar: OHLCVBar) -> list[Fill]:
        """
        Evaluate all resting and pending orders against the given price bar.

        Args:
            bar: The current market bar.

        Returns:
            List of generated Fill objects.
        """
        new_fills: list[Fill] = []

        # 1. Process pending market orders first
        orders_to_process = list(self._pending_orders)
        self._pending_orders.clear()

        for order in orders_to_process:
            target_price = bar.open if self.fill_on_next_open else bar.close
            fill_price = self.slippage_model.calculate_fill_price(
                target_price=target_price,
                side=order.side,
                quantity=order.quantity,
                bar_open=bar.open,
                bar_high=bar.high,
                bar_low=bar.low,
                bar_close=bar.close,
                bar_volume=bar.volume,
            )

            cost_breakdown = self.cost_model.calculate_cost(
                asset=order.asset,
                side=order.side,
                quantity=order.quantity,
                fill_price=fill_price,
            )

            fill = Fill(
                fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
                order_id=order.order_id,
                asset=order.asset,
                side=order.side,
                quantity=order.quantity,
                price=fill_price,
                commission=cost_breakdown.total_cost,
                timestamp=bar.timestamp,
            )
            new_fills.append(fill)
            self._executed_fills.append(fill)

        # 2. Process resting limit & stop orders
        remaining_limit_orders: list[Order] = []
        for order in self._active_limit_orders:
            match_result = self._match_resting_order(order, bar)
            if match_result.is_filled and match_result.fill:
                new_fills.append(match_result.fill)
                self._executed_fills.append(match_result.fill)
            else:
                remaining_limit_orders.append(order)

        self._active_limit_orders = remaining_limit_orders
        return new_fills

    def _match_resting_order(self, order: Order, bar: OHLCVBar) -> MatchResult:
        """Evaluate a single limit or stop order against bar extremes."""
        # ── Limit Order Matching ──
        if order.order_type == OrderType.LIMIT:
            if order.limit_price is None:
                return MatchResult(order=order, is_filled=False, rejection_reason="No limit price")

            if order.side == Side.BUY:
                # Buy limit triggers if market trades at or below limit price
                if bar.low <= order.limit_price:
                    # If bar opened below limit price, favorable gap fill at open
                    base_price = min(bar.open, order.limit_price)
                    fill_price = self.slippage_model.calculate_fill_price(
                        target_price=base_price,
                        side=order.side,
                        quantity=order.quantity,
                        bar_open=bar.open,
                        bar_high=bar.high,
                        bar_low=bar.low,
                        bar_close=bar.close,
                        bar_volume=bar.volume,
                    )
                    cost = self.cost_model.calculate_cost(
                        asset=order.asset, side=order.side, quantity=order.quantity, fill_price=fill_price
                    )
                    fill = Fill(
                        fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
                        order_id=order.order_id,
                        asset=order.asset,
                        side=order.side,
                        quantity=order.quantity,
                        price=fill_price,
                        commission=cost.total_cost,
                        timestamp=bar.timestamp,
                    )
                    return MatchResult(order=order, fill=fill, is_filled=True)

            elif order.side == Side.SELL:
                # Sell limit triggers if market trades at or above limit price
                if bar.high >= order.limit_price:
                    base_price = max(bar.open, order.limit_price)
                    fill_price = self.slippage_model.calculate_fill_price(
                        target_price=base_price,
                        side=order.side,
                        quantity=order.quantity,
                        bar_open=bar.open,
                        bar_high=bar.high,
                        bar_low=bar.low,
                        bar_close=bar.close,
                        bar_volume=bar.volume,
                    )
                    cost = self.cost_model.calculate_cost(
                        asset=order.asset, side=order.side, quantity=order.quantity, fill_price=fill_price
                    )
                    fill = Fill(
                        fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
                        order_id=order.order_id,
                        asset=order.asset,
                        side=order.side,
                        quantity=order.quantity,
                        price=fill_price,
                        commission=cost.total_cost,
                        timestamp=bar.timestamp,
                    )
                    return MatchResult(order=order, fill=fill, is_filled=True)

        # ── Stop Order Matching ──
        elif order.order_type == OrderType.STOP:
            if order.stop_price is None:
                return MatchResult(order=order, is_filled=False, rejection_reason="No stop price")

            if order.side == Side.BUY and bar.high >= order.stop_price:
                # Gap up handled: fill at open or stop_price
                base_price = max(bar.open, order.stop_price)
                fill_price = self.slippage_model.calculate_fill_price(
                    target_price=base_price,
                    side=order.side,
                    quantity=order.quantity,
                    bar_open=bar.open,
                    bar_high=bar.high,
                    bar_low=bar.low,
                    bar_close=bar.close,
                    bar_volume=bar.volume,
                )
                cost = self.cost_model.calculate_cost(
                    asset=order.asset, side=order.side, quantity=order.quantity, fill_price=fill_price
                )
                fill = Fill(
                    fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
                    order_id=order.order_id,
                    asset=order.asset,
                    side=order.side,
                    quantity=order.quantity,
                    price=fill_price,
                    commission=cost.total_cost,
                    timestamp=bar.timestamp,
                )
                return MatchResult(order=order, fill=fill, is_filled=True)

            elif order.side == Side.SELL and bar.low <= order.stop_price:
                # Gap down handled
                base_price = min(bar.open, order.stop_price)
                fill_price = self.slippage_model.calculate_fill_price(
                    target_price=base_price,
                    side=order.side,
                    quantity=order.quantity,
                    bar_open=bar.open,
                    bar_high=bar.high,
                    bar_low=bar.low,
                    bar_close=bar.close,
                    bar_volume=bar.volume,
                )
                cost = self.cost_model.calculate_cost(
                    asset=order.asset, side=order.side, quantity=order.quantity, fill_price=fill_price
                )
                fill = Fill(
                    fill_id=f"FILL-{uuid.uuid4().hex[:8].upper()}",
                    order_id=order.order_id,
                    asset=order.asset,
                    side=order.side,
                    quantity=order.quantity,
                    price=fill_price,
                    commission=cost.total_cost,
                    timestamp=bar.timestamp,
                )
                return MatchResult(order=order, fill=fill, is_filled=True)

        return MatchResult(order=order, is_filled=False)

    @property
    def open_orders_count(self) -> int:
        return len(self._pending_orders) + len(self._active_limit_orders)

    @property
    def total_executed_fills(self) -> int:
        return len(self._executed_fills)
