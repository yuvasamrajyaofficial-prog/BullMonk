"""
Transaction Costs and Slippage Models for Algorithmic Backtesting.

Supports authentic Indian market taxation & fees (NSE/BSE):
- Securities Transaction Tax (STT / CTT)
- Exchange Turnover Fees
- SEBI Charges
- Stamp Duty
- Goods and Services Tax (GST @ 18%)
- Brokerage (Flat per order or percentage)
- Multi-asset generic models (Crypto & Forex flat/spread models)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

from core.enums import AssetClass, Side
from core.models import Asset, Order


# ──────────────────────────────────────────────
# Slippage Models
# ──────────────────────────────────────────────

class SlippageModel(ABC):
    """Abstract interface for execution price slippage."""

    @abstractmethod
    def calculate_fill_price(
        self,
        target_price: Decimal,
        side: Side,
        quantity: Decimal,
        bar_open: Decimal,
        bar_high: Decimal,
        bar_low: Decimal,
        bar_close: Decimal,
        bar_volume: int,
    ) -> Decimal:
        """
        Compute the executed fill price after modeling market slippage.

        Args:
            target_price: Desired execution price (e.g. bar open or limit price).
            side: BUY or SELL.
            quantity: Order size.
            bar_open: Current bar open.
            bar_high: Current bar high.
            bar_low: Current bar low.
            bar_close: Current bar close.
            bar_volume: Current bar volume in shares/contracts.

        Returns:
            Adjusted fill price (higher for buys, lower for sells).
        """


class ZeroSlippageModel(SlippageModel):
    """Zero slippage model for pure mathematical backtesting baseline."""

    def calculate_fill_price(
        self,
        target_price: Decimal,
        side: Side,
        quantity: Decimal,
        bar_open: Decimal,
        bar_high: Decimal,
        bar_low: Decimal,
        bar_close: Decimal,
        bar_volume: int,
    ) -> Decimal:
        return target_price


class FixedBpsSlippageModel(SlippageModel):
    """
    Fixed basis points slippage model.
    E.g. 5 bps = 0.05% penalty on entry/exit price.
    """

    def __init__(self, basis_points: float = 5.0) -> None:
        if basis_points < 0:
            raise ValueError("basis_points must be non-negative.")
        self.basis_points = basis_points
        self._multiplier = Decimal(str(basis_points / 10000.0))

    def calculate_fill_price(
        self,
        target_price: Decimal,
        side: Side,
        quantity: Decimal,
        bar_open: Decimal,
        bar_high: Decimal,
        bar_low: Decimal,
        bar_close: Decimal,
        bar_volume: int,
    ) -> Decimal:
        penalty = target_price * self._multiplier
        if side == Side.BUY:
            return target_price + penalty
        else:
            return max(target_price - penalty, Decimal("0.01"))


class VolumeShareSlippageModel(SlippageModel):
    """
    Market impact slippage proportional to the order's share of bar volume.
    Penalty = base_bps + impact_factor * (order_qty / bar_vol).
    Clamped to bar High (for Buys) and bar Low (for Sells).
    """

    def __init__(self, base_bps: float = 2.0, impact_factor: float = 0.1) -> None:
        self.base_bps = Decimal(str(base_bps / 10000.0))
        self.impact_factor = Decimal(str(impact_factor))

    def calculate_fill_price(
        self,
        target_price: Decimal,
        side: Side,
        quantity: Decimal,
        bar_open: Decimal,
        bar_high: Decimal,
        bar_low: Decimal,
        bar_close: Decimal,
        bar_volume: int,
    ) -> Decimal:
        vol = Decimal(str(max(bar_volume, 1)))
        participation_rate = quantity / vol
        slippage_pct = self.base_bps + (self.impact_factor * participation_rate)

        if side == Side.BUY:
            price = target_price * (Decimal("1") + slippage_pct)
            return min(price, bar_high)
        else:
            price = target_price * (Decimal("1") - slippage_pct)
            return max(price, bar_low, Decimal("0.01"))


# ──────────────────────────────────────────────
# Fee Breakdown & Cost Models
# ──────────────────────────────────────────────

@dataclass(frozen=True)
class TransactionCostBreakdown:
    """Itemized breakdown of all execution costs and taxes."""

    brokerage: Decimal
    stt_ctt: Decimal
    exchange_turnover_fee: Decimal
    sebi_turnover_fee: Decimal
    stamp_duty: Decimal
    gst: Decimal
    total_cost: Decimal


class CostModel(ABC):
    """Abstract interface for trade commission and statutory transaction costs."""

    @abstractmethod
    def calculate_cost(
        self,
        asset: Asset,
        side: Side,
        quantity: Decimal,
        fill_price: Decimal,
        is_intraday: bool = False,
    ) -> TransactionCostBreakdown:
        """Calculate the total transaction costs for a single fill."""


class ZeroCostModel(CostModel):
    """Zero fees baseline model."""

    def calculate_cost(
        self,
        asset: Asset,
        side: Side,
        quantity: Decimal,
        fill_price: Decimal,
        is_intraday: bool = False,
    ) -> TransactionCostBreakdown:
        zero = Decimal("0")
        return TransactionCostBreakdown(
            brokerage=zero,
            stt_ctt=zero,
            exchange_turnover_fee=zero,
            sebi_turnover_fee=zero,
            stamp_duty=zero,
            gst=zero,
            total_cost=zero,
        )


class IndianMarketCostModel(CostModel):
    """
    Standard Indian Market Statutory Fee Structure (NSE / BSE).
    
    Applicable rules:
    - Brokerage: Default flat ₹20 per executed order (discount broker model)
    - STT (Securities Transaction Tax):
      * Equity Delivery: 0.1% on turnover (Buy & Sell)
      * Equity Intraday: 0.025% on turnover (Sell only)
      * Equity / Index Futures: 0.0125% on turnover (Sell only)
      * Equity / Index Options: 0.0625% on premium turnover (Sell only)
    - Exchange Turnover Charges:
      * Equity Cash: 0.00345%
      * Futures: 0.0019%
      * Options: 0.05% of premium
    - SEBI Turnover Charges: ₹10 per crore (0.0001%)
    - Stamp Duty (Buy orders only):
      * Equity Delivery: 0.015%
      * Equity Intraday: 0.003%
      * Futures: 0.002%
      * Options: 0.003%
    - GST: 18% on (Brokerage + Exchange fees + SEBI fees)
    """

    def __init__(self, flat_brokerage_per_order: Decimal = Decimal("20.0")) -> None:
        self.flat_brokerage = flat_brokerage_per_order

    def calculate_cost(
        self,
        asset: Asset,
        side: Side,
        quantity: Decimal,
        fill_price: Decimal,
        is_intraday: bool = False,
    ) -> TransactionCostBreakdown:
        turnover = quantity * fill_price

        # 1. Brokerage (capped at 0.03% of turnover or flat ₹20)
        percentage_brokerage = turnover * Decimal("0.0003")
        brokerage = min(self.flat_brokerage, percentage_brokerage)

        # 2. STT / CTT
        stt = Decimal("0")
        if asset.asset_class == AssetClass.EQUITY:
            if not is_intraday:
                stt = turnover * Decimal("0.001")  # 0.1% buy & sell
            elif side == Side.SELL:
                stt = turnover * Decimal("0.00025")  # 0.025% sell only
        elif asset.asset_class == AssetClass.FUTURES:
            if side == Side.SELL:
                stt = turnover * Decimal("0.000125")  # 0.0125% sell only
        elif asset.asset_class == AssetClass.OPTIONS:
            if side == Side.SELL:
                stt = turnover * Decimal("0.000625")  # 0.0625% of premium

        # 3. Exchange Turnover Charges
        if asset.asset_class == AssetClass.EQUITY:
            exchange_fee = turnover * Decimal("0.0000345")  # 0.00345%
        elif asset.asset_class == AssetClass.FUTURES:
            exchange_fee = turnover * Decimal("0.000019")   # 0.0019%
        elif asset.asset_class == AssetClass.OPTIONS:
            exchange_fee = turnover * Decimal("0.0005")     # 0.05%
        else:
            exchange_fee = turnover * Decimal("0.00003")

        # 4. SEBI Turnover Charges (₹10 / crore = 0.0001%)
        sebi_fee = turnover * Decimal("0.000001")

        # 5. Stamp Duty (on BUY only)
        stamp_duty = Decimal("0")
        if side == Side.BUY:
            if asset.asset_class == AssetClass.EQUITY:
                rate = Decimal("0.00015") if not is_intraday else Decimal("0.00003")
                stamp_duty = turnover * rate
            elif asset.asset_class == AssetClass.FUTURES:
                stamp_duty = turnover * Decimal("0.00002")
            elif asset.asset_class == AssetClass.OPTIONS:
                stamp_duty = turnover * Decimal("0.00003")

        # 6. GST @ 18% on (Brokerage + Exchange Fee + SEBI Fee)
        taxable_services = brokerage + exchange_fee + sebi_fee
        gst = taxable_services * Decimal("0.18")

        total = brokerage + stt + exchange_fee + sebi_fee + stamp_duty + gst

        return TransactionCostBreakdown(
            brokerage=round(brokerage, 2),
            stt_ctt=round(stt, 2),
            exchange_turnover_fee=round(exchange_fee, 2),
            sebi_turnover_fee=round(sebi_fee, 4),
            stamp_duty=round(stamp_duty, 2),
            gst=round(gst, 2),
            total_cost=round(total, 2),
        )


class FlatPercentageCostModel(CostModel):
    """Simple flat percentage model suitable for Crypto / Forex (e.g. 0.04% maker/taker)."""

    def __init__(self, fee_percentage: float = 0.04) -> None:
        self.fee_rate = Decimal(str(fee_percentage / 100.0))

    def calculate_cost(
        self,
        asset: Asset,
        side: Side,
        quantity: Decimal,
        fill_price: Decimal,
        is_intraday: bool = False,
    ) -> TransactionCostBreakdown:
        turnover = quantity * fill_price
        total = round(turnover * self.fee_rate, 4)
        zero = Decimal("0")
        return TransactionCostBreakdown(
            brokerage=total,
            stt_ctt=zero,
            exchange_turnover_fee=zero,
            sebi_turnover_fee=zero,
            stamp_duty=zero,
            gst=zero,
            total_cost=total,
        )
