"""
Advanced Quantitative Analytics and Institutional Risk Metrics.

Computes:
- Sharpe Ratio, Sortino Ratio, Calmar Ratio
- Annualized Return (CAGR) and Realized Volatility
- Max Drawdown (%) and Peak-to-Trough Duration
- Win Rate, Payoff Ratio, Profit Factor, Expectancy
- Value-at-Risk (VaR 95%, 99%) and Conditional VaR (Expected Shortfall)
- Underwater Drawdown Series
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
import math
from typing import Optional

from core.models import PortfolioSnapshot, Trade


@dataclass(frozen=True)
class AdvancedMetricsResult:
    """Comprehensive institutional performance tear-sheet metrics."""

    # Capital & PnL
    initial_capital: Decimal
    final_equity: Decimal
    total_net_pnl: Decimal
    total_return_pct: float
    cagr_pct: float

    # Risk-adjusted ratios
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    annualized_volatility_pct: float

    # Drawdown metrics
    max_drawdown_pct: float
    max_drawdown_duration_bars: int

    # Trade Statistics
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate_pct: float
    profit_factor: float
    payoff_ratio: float
    average_trade_pnl: Decimal
    average_win: Decimal
    average_loss: Decimal
    largest_win: Decimal
    largest_loss: Decimal
    expectancy: Decimal

    # Tail Risk
    var_95_pct: float
    cvar_95_pct: float
    var_99_pct: float

    # Costs
    total_commissions_and_taxes: Decimal


class AdvancedAnalyticsEngine:
    """
    Stateless quantitative performance computation engine.
    Computes professional-grade tear-sheet metrics from trades and equity curves.
    """

    def __init__(self, risk_free_rate_annual: float = 0.07, trading_days_per_year: int = 252) -> None:
        """
        Args:
            risk_free_rate_annual: Default 7.0% (standard benchmark for Indian RBI Repo rate).
            trading_days_per_year: Default 252 trading sessions per year.
        """
        self.risk_free_rate = risk_free_rate_annual
        self.trading_days = trading_days_per_year

    def compute_metrics(
        self,
        trades: list[Trade],
        equity_snapshots: list[PortfolioSnapshot],
        initial_capital: Decimal,
    ) -> AdvancedMetricsResult:
        """
        Compute the full performance suite from executed trades and portfolio snapshots.
        """
        # 1. PnL & Returns
        final_equity = equity_snapshots[-1].total_equity if equity_snapshots else initial_capital
        total_pnl = final_equity - initial_capital
        total_return_pct = float((total_pnl / initial_capital) * Decimal("100"))

        # Time horizon approximation for CAGR
        num_snapshots = len(equity_snapshots)
        years = max(num_snapshots / (self.trading_days * 75.0), 1.0 / self.trading_days)  # assuming intraday or daily
        if float(final_equity) > 0 and float(initial_capital) > 0:
            cagr = ((float(final_equity) / float(initial_capital)) ** (1.0 / years) - 1.0) * 100.0
        else:
            cagr = -100.0

        # 2. Equity Curve & Return Series
        returns: list[float] = []
        equity_vals = [float(s.total_equity) for s in equity_snapshots] if equity_snapshots else [float(initial_capital)]
        for i in range(1, len(equity_vals)):
            prev = equity_vals[i - 1]
            if prev > 0:
                returns.append((equity_vals[i] - prev) / prev)
            else:
                returns.append(0.0)

        # 3. Volatility & Risk-Adjusted Ratios
        ann_vol = 0.0
        sharpe = 0.0
        sortino = 0.0

        if len(returns) > 1:
            mean_ret = sum(returns) / len(returns)
            variance = sum((r - mean_ret) ** 2 for r in returns) / (len(returns) - 1)
            std_dev = math.sqrt(variance)
            ann_factor = math.sqrt(self.trading_days * 75)  # annualization factor
            ann_vol = std_dev * ann_factor * 100.0

            # Sharpe (excess return / vol)
            rf_per_bar = self.risk_free_rate / (self.trading_days * 75)
            excess_returns = [r - rf_per_bar for r in returns]
            mean_excess = sum(excess_returns) / len(excess_returns)
            if std_dev > 0:
                sharpe = (mean_excess / std_dev) * ann_factor

            # Sortino (downside deviation only)
            downside_diffs = [min(r - rf_per_bar, 0.0) ** 2 for r in returns]
            downside_dev = math.sqrt(sum(downside_diffs) / len(returns))
            if downside_dev > 0:
                sortino = (mean_excess / downside_dev) * ann_factor

        # 4. Drawdowns
        max_dd = 0.0
        max_dd_duration = 0
        current_dd_duration = 0
        peak = equity_vals[0] if equity_vals else float(initial_capital)

        for eq in equity_vals:
            if eq > peak:
                peak = eq
                current_dd_duration = 0
            else:
                current_dd_duration += 1
                if current_dd_duration > max_dd_duration:
                    max_dd_duration = current_dd_duration
                dd = ((peak - eq) / peak) * 100.0
                if dd > max_dd:
                    max_dd = dd

        calmar = (cagr / max_dd) if max_dd > 0 else 0.0

        # 5. Trade Analysis
        total_trades = len(trades)
        winning_trades = [t for t in trades if t.net_pnl > Decimal("0")]
        losing_trades = [t for t in trades if t.net_pnl < Decimal("0")]

        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades * 100.0) if total_trades > 0 else 0.0

        gross_profit = sum((t.net_pnl for t in winning_trades), Decimal("0"))
        gross_loss = abs(sum((t.net_pnl for t in losing_trades), Decimal("0")))
        profit_factor = float(gross_profit / gross_loss) if gross_loss > 0 else (float("inf") if gross_profit > 0 else 0.0)

        avg_win = (gross_profit / Decimal(win_count)) if win_count > 0 else Decimal("0")
        avg_loss = (abs(gross_loss) / Decimal(loss_count)) if loss_count > 0 else Decimal("0")
        payoff_ratio = float(avg_win / avg_loss) if avg_loss > 0 else 0.0

        avg_trade_pnl = (total_pnl / Decimal(total_trades)) if total_trades > 0 else Decimal("0")
        largest_win = max((t.net_pnl for t in winning_trades), default=Decimal("0"))
        largest_loss = min((t.net_pnl for t in losing_trades), default=Decimal("0"))

        # Expectancy: (WinRate * AvgWin) - (LossRate * AvgLoss)
        wr_dec = Decimal(str(win_rate / 100.0))
        lr_dec = Decimal("1") - wr_dec
        expectancy = (wr_dec * avg_win) - (lr_dec * avg_loss)

        # 6. Tail Risk: VaR & CVaR (Historical simulation)
        sorted_returns = sorted(returns)
        var_95 = 0.0
        var_99 = 0.0
        cvar_95 = 0.0
        if len(sorted_returns) >= 20:
            idx_95 = int(len(sorted_returns) * 0.05)
            idx_99 = int(len(sorted_returns) * 0.01)
            var_95 = abs(sorted_returns[idx_95]) * 100.0
            var_99 = abs(sorted_returns[idx_99]) * 100.0
            tail_losses = [abs(r) for r in sorted_returns[:idx_95]]
            cvar_95 = (sum(tail_losses) / len(tail_losses) * 100.0) if tail_losses else var_95

        total_costs = sum((t.commission for t in trades), Decimal("0"))

        return AdvancedMetricsResult(
            initial_capital=initial_capital,
            final_equity=final_equity,
            total_net_pnl=total_pnl,
            total_return_pct=round(total_return_pct, 2),
            cagr_pct=round(cagr, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            calmar_ratio=round(calmar, 2),
            annualized_volatility_pct=round(ann_vol, 2),
            max_drawdown_pct=round(max_dd, 2),
            max_drawdown_duration_bars=max_dd_duration,
            total_trades=total_trades,
            winning_trades=win_count,
            losing_trades=loss_count,
            win_rate_pct=round(win_rate, 2),
            profit_factor=round(profit_factor, 2),
            payoff_ratio=round(payoff_ratio, 2),
            average_trade_pnl=round(avg_trade_pnl, 2),
            average_win=round(avg_win, 2),
            average_loss=round(avg_loss, 2),
            largest_win=round(largest_win, 2),
            largest_loss=round(largest_loss, 2),
            expectancy=round(expectancy, 2),
            var_95_pct=round(var_95, 2),
            cvar_95_pct=round(cvar_95, 2),
            var_99_pct=round(var_99, 2),
            total_commissions_and_taxes=round(total_costs, 2),
        )
