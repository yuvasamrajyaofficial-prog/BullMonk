"""
Analytics engine — performance metrics computation.

Phase 1: Core statistical metrics computed from a list of Trade objects
or equity curve. No external dependencies beyond the standard library
and the decimal module.

Future phases will add:
- Sharpe / Sortino / Calmar ratios
- Monte Carlo simulation
- Walk-forward analysis reports
- Visualisation output
"""

from __future__ import annotations

import logging
import math
from decimal import Decimal
from statistics import mean, stdev
from typing import Optional

from core.models import Trade

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Computes performance metrics from completed trade records.

    All metrics are computed from the trade list provided to each method.
    The class itself is stateless — it can be used functionally.
    """

    # ──────────────────────────────────────────────
    # Basic metrics
    # ──────────────────────────────────────────────

    def total_net_pnl(self, trades: list[Trade]) -> Decimal:
        """Sum of net P&L across all trades."""
        return sum((t.net_pnl for t in trades), Decimal("0"))

    def total_gross_pnl(self, trades: list[Trade]) -> Decimal:
        """Sum of gross P&L across all trades."""
        return sum((t.gross_pnl for t in trades), Decimal("0"))

    def total_commission(self, trades: list[Trade]) -> Decimal:
        """Total commission paid across all trades."""
        return sum((t.commission for t in trades), Decimal("0"))

    def win_rate(self, trades: list[Trade]) -> float:
        """Fraction of trades with positive net P&L."""
        if not trades:
            return 0.0
        winners = sum(1 for t in trades if t.net_pnl > Decimal("0"))
        return winners / len(trades)

    def average_win(self, trades: list[Trade]) -> Decimal:
        """Average net P&L of winning trades."""
        winners = [t.net_pnl for t in trades if t.net_pnl > Decimal("0")]
        if not winners:
            return Decimal("0")
        return sum(winners, Decimal("0")) / Decimal(len(winners))

    def average_loss(self, trades: list[Trade]) -> Decimal:
        """Average net P&L of losing trades (returned as a negative number)."""
        losers = [t.net_pnl for t in trades if t.net_pnl < Decimal("0")]
        if not losers:
            return Decimal("0")
        return sum(losers, Decimal("0")) / Decimal(len(losers))

    def profit_factor(self, trades: list[Trade]) -> float:
        """Ratio of gross profits to gross losses. Returns inf if no losses."""
        gross_profit = float(
            sum((t.net_pnl for t in trades if t.net_pnl > Decimal("0")), Decimal("0"))
        )
        gross_loss = abs(
            float(
                sum(
                    (t.net_pnl for t in trades if t.net_pnl < Decimal("0")),
                    Decimal("0"),
                )
            )
        )
        if gross_loss == 0.0:
            return math.inf
        return gross_profit / gross_loss

    def max_consecutive_wins(self, trades: list[Trade]) -> int:
        """Maximum consecutive winning trades."""
        return self._max_consecutive(trades, winning=True)

    def max_consecutive_losses(self, trades: list[Trade]) -> int:
        """Maximum consecutive losing trades."""
        return self._max_consecutive(trades, winning=False)

    # ──────────────────────────────────────────────
    # Drawdown
    # ──────────────────────────────────────────────

    def max_drawdown(self, equity_curve: list[Decimal]) -> tuple[Decimal, float]:
        """
        Compute maximum drawdown from an equity curve.

        Args:
            equity_curve: Time-ordered list of equity values.

        Returns:
            Tuple of (max_drawdown_abs, max_drawdown_pct).
            max_drawdown_pct is in percentage points (e.g. 15.3 means 15.3%).
        """
        if not equity_curve:
            return Decimal("0"), 0.0

        peak = equity_curve[0]
        max_dd_abs = Decimal("0")
        max_dd_pct = 0.0

        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd_abs = peak - equity
            if peak > Decimal("0"):
                dd_pct = float(dd_abs / peak) * 100.0
            else:
                dd_pct = 0.0
            if dd_abs > max_dd_abs:
                max_dd_abs = dd_abs
                max_dd_pct = dd_pct

        return max_dd_abs, max_dd_pct

    # ──────────────────────────────────────────────
    # Summary report
    # ──────────────────────────────────────────────

    def generate_summary(
        self,
        trades: list[Trade],
        equity_curve: Optional[list[Decimal]] = None,
    ) -> dict:
        """
        Generate a complete performance summary dictionary.

        Args:
            trades:       List of completed Trade objects.
            equity_curve: Optional equity curve for drawdown calculation.

        Returns:
            Dictionary with all computed metrics.
        """
        dd_abs, dd_pct = (Decimal("0"), 0.0)
        if equity_curve:
            dd_abs, dd_pct = self.max_drawdown(equity_curve)

        summary = {
            "total_trades": len(trades),
            "net_pnl": float(self.total_net_pnl(trades)),
            "gross_pnl": float(self.total_gross_pnl(trades)),
            "total_commission": float(self.total_commission(trades)),
            "win_rate": round(self.win_rate(trades) * 100, 2),
            "profit_factor": round(self.profit_factor(trades), 4),
            "average_win": float(self.average_win(trades)),
            "average_loss": float(self.average_loss(trades)),
            "max_consecutive_wins": self.max_consecutive_wins(trades),
            "max_consecutive_losses": self.max_consecutive_losses(trades),
            "max_drawdown_abs": float(dd_abs),
            "max_drawdown_pct": round(dd_pct, 4),
        }

        logger.debug("AnalyticsEngine.generate_summary: %s", summary)
        return summary

    # ──────────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────────

    @staticmethod
    def _max_consecutive(trades: list[Trade], *, winning: bool) -> int:
        max_streak = 0
        current_streak = 0
        for trade in trades:
            is_win = trade.net_pnl > Decimal("0")
            if is_win == winning:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        return max_streak
