"""
Execution-layer domain models.

These supplement the core Order/Fill models with execution-specific
routing, slippage, and commission information.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from core.enums import OrderType, Side
from core.models import Asset


class ExecutionReport(BaseModel):
    """
    A normalised execution report combining order and fill data.

    Produced by the executor after a fill is confirmed.
    """

    model_config = {"frozen": True}

    order_id: str
    broker_order_id: str
    asset: Asset
    side: Side
    ordered_quantity: Decimal
    filled_quantity: Decimal
    average_fill_price: Decimal
    slippage: Decimal = Field(
        default=Decimal("0"),
        description="Difference between expected and actual fill price",
    )
    commission: Decimal = Field(default=Decimal("0"))
    net_pnl_impact: Decimal = Field(default=Decimal("0"))
    timestamp: datetime


class CommissionSchedule(BaseModel):
    """
    Defines how commissions are calculated for a broker/instrument.

    Phase 1: fixed per-order or percentage-of-value models.
    """

    broker_name: str
    per_order_flat: Decimal = Field(default=Decimal("0"), description="Fixed fee per order")
    pct_of_value: Decimal = Field(
        default=Decimal("0"),
        description="Commission as % of order notional (e.g. 0.03 for 0.03%)",
    )
    min_commission: Decimal = Field(
        default=Decimal("0"),
        description="Minimum commission per order",
    )
    max_commission: Optional[Decimal] = Field(
        default=None,
        description="Maximum commission per order cap (None = no cap)",
    )

    def calculate(self, quantity: Decimal, price: Decimal) -> Decimal:
        """
        Calculate the commission for a given trade.

        Args:
            quantity: Number of units/lots traded.
            price:    Fill price.

        Returns:
            Commission amount in the settlement currency.
        """
        notional = quantity * price
        commission = self.per_order_flat + (notional * self.pct_of_value / Decimal("100"))
        commission = max(commission, self.min_commission)
        if self.max_commission is not None:
            commission = min(commission, self.max_commission)
        return commission
