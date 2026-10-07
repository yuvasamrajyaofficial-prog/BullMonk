"""
Risk Manager.

The risk manager acts as a gatekeeper between signal generation and
order submission. Every order must pass through the risk manager
before it is sent to the broker.

Phase 1: Synchronous, in-process risk checks.
Phase 2: Can be extended to async, multi-threaded, or distributed checks.

Risk checks implemented:
1. Order value cap
2. Max position size (% of equity)
3. Max daily loss (% of starting equity)
4. Max open positions count
5. Asset class whitelist
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.enums import AssetClass, RiskDecisionType
from core.events import EventBus, RiskBreachEvent
from core.models import Account, Order, Position, RiskDecision, RiskLimits

logger = logging.getLogger(__name__)


class RiskManager:
    """
    Stateful risk manager.

    Maintains running counts and P&L figures and evaluates each order
    against configured risk limits before allowing execution.
    """

    def __init__(
        self,
        limits: RiskLimits,
        event_bus: EventBus,
    ) -> None:
        """
        Args:
            limits:    Risk configuration.
            event_bus: Used to publish RiskBreachEvent when limits are hit.
        """
        self._limits = limits
        self._event_bus = event_bus
        self._daily_realized_pnl: Decimal = Decimal("0")
        self._open_position_count: int = 0
        self._session_start_equity: Optional[Decimal] = None

        logger.info(
            "RiskManager initialized: max_daily_loss_pct=%.2f%% "
            "max_positions=%d max_position_size_pct=%.2f%%",
            limits.max_daily_loss_pct,
            limits.max_open_positions,
            limits.max_position_size_pct,
        )

    # ──────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────

    def evaluate_order(
        self,
        order: Order,
        account: Account,
        open_positions: list[Position],
    ) -> RiskDecision:
        """
        Evaluate whether an order should be approved, modified, or rejected.

        Args:
            order:          The proposed order.
            account:        Current account state (for equity and balance).
            open_positions: Current open positions (for count and concentration).

        Returns:
            RiskDecision with APPROVED, MODIFIED, or REJECTED verdict.
        """
        balance = account.get_balance()
        if balance is None:
            return self._reject(order.order_id, "No balance information available.")

        total_equity = balance.total_equity
        if self._session_start_equity is None:
            self._session_start_equity = total_equity

        # ── Check 1: Asset class whitelist ──
        allowed = self._limits.allowed_asset_classes
        if allowed and order.asset.asset_class not in allowed:
            return self._reject(
                order.order_id,
                f"Asset class {order.asset.asset_class.value} not in allowed list.",
            )

        # ── Check 2: Max open positions ──
        current_position_count = len([p for p in open_positions if p.quantity > Decimal("0")])
        if current_position_count >= self._limits.max_open_positions:
            return self._reject(
                order.order_id,
                f"Max open positions ({self._limits.max_open_positions}) already reached.",
            )

        # ── Check 3: Max order value ──
        if order.limit_price is not None:
            order_value = order.quantity * order.limit_price
        else:
            order_value = Decimal("0")  # Market order — value unknown pre-fill

        if (
            self._limits.max_order_value is not None
            and order_value > self._limits.max_order_value
        ):
            return self._reject(
                order.order_id,
                f"Order value {order_value:.2f} exceeds max "
                f"{self._limits.max_order_value:.2f}.",
            )

        # ── Check 4: Max position size % of equity ──
        if total_equity > Decimal("0") and order_value > Decimal("0"):
            position_pct = (order_value / total_equity) * Decimal("100")
            if float(position_pct) > self._limits.max_position_size_pct:
                return self._reject(
                    order.order_id,
                    f"Order would exceed max position size "
                    f"({position_pct:.2f}% > {self._limits.max_position_size_pct:.2f}%).",
                )

        # ── Check 5: Max daily loss ──
        if self._session_start_equity and self._session_start_equity > Decimal("0"):
            daily_loss_pct = float(
                (-self._daily_realized_pnl / self._session_start_equity) * Decimal("100")
            )
            if daily_loss_pct >= self._limits.max_daily_loss_pct:
                self._publish_risk_breach(
                    "MAX_DAILY_LOSS",
                    daily_loss_pct,
                    self._limits.max_daily_loss_pct,
                )
                return self._reject(
                    order.order_id,
                    f"Daily loss limit breached: {daily_loss_pct:.2f}% "
                    f">= {self._limits.max_daily_loss_pct:.2f}%.",
                )

        logger.debug(
            "RiskManager.evaluate_order: APPROVED order_id=%s asset=%s side=%s qty=%s",
            order.order_id,
            order.asset,
            order.side.value,
            order.quantity,
        )
        return RiskDecision(decision=RiskDecisionType.APPROVED, order_id=order.order_id)

    def record_pnl(self, realized_pnl: Decimal) -> None:
        """
        Update the running daily P&L figure.

        Args:
            realized_pnl: Change in realized P&L (can be positive or negative).
        """
        self._daily_realized_pnl += realized_pnl
        logger.debug(
            "RiskManager.record_pnl: delta=%s cumulative_daily_pnl=%s",
            realized_pnl,
            self._daily_realized_pnl,
        )

    def reset_daily_pnl(self) -> None:
        """Reset daily P&L tracker. Call at the start of each trading day."""
        self._daily_realized_pnl = Decimal("0")
        self._session_start_equity = None
        logger.info("RiskManager: daily P&L counters reset.")

    @property
    def daily_realized_pnl(self) -> Decimal:
        return self._daily_realized_pnl

    @property
    def limits(self) -> RiskLimits:
        return self._limits

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    def _reject(self, order_id: str, reason: str) -> RiskDecision:
        logger.warning("RiskManager.REJECTED order_id=%s reason=%s", order_id, reason)
        self._publish_risk_breach(reason, 0.0, 0.0)
        return RiskDecision(
            decision=RiskDecisionType.REJECTED,
            order_id=order_id,
            reason=reason,
        )

    def _publish_risk_breach(
        self, limit_name: str, current: float, limit: float
    ) -> None:
        self._event_bus.publish(
            RiskBreachEvent(
                source="RiskManager",
                payload={
                    "limit_name": limit_name,
                    "current": current,
                    "limit": limit,
                },
            )
        )
