"""
Institutional Quantitative Performance Tear Sheet Formatter.

Generates structured ASCII tear-sheets and performance summaries:
- Returns & Capital
- Risk-adjusted ratios (Sharpe, Sortino, Calmar)
- Drawdowns & Duration
- Trade Statistics (Win rate, Expectancy, Profit Factor)
- Tail Risk (VaR 95%, CVaR 95%)
- Statutory Cost & Slippage friction audit
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from analytics.advanced_metrics import AdvancedMetricsResult


class TearSheetFormatter:
    """Formats performance metrics into professional terminal tables."""

    @staticmethod
    def format_terminal_report(metrics: AdvancedMetricsResult, strategy_id: str, symbol: str) -> str:
        border = "=" * 72
        div = "-" * 72

        lines = [
            "",
            border,
            f"  BULLMONK QUANTITATIVE PERFORMANCE TEARSHEET - {strategy_id.upper()}",
            f"  Asset: {symbol}  |  Base Currency: INR  |  Benchmark: NIFTY 50",
            border,
            "  PORTFOLIO CAPITAL & RETURNS",
            div,
            f"  Initial Capital:          INR {metrics.initial_capital:,.2f}",
            f"  Final Equity:             INR {metrics.final_equity:,.2f}",
            f"  Net Total Profit/Loss:    INR {metrics.total_net_pnl:,.2f} ({metrics.total_return_pct:+.2f}%)",
            f"  Compounded Annual Return: {metrics.cagr_pct:+.2f}%",
            "",
            "  RISK-ADJUSTED PERFORMANCE",
            div,
            f"  Sharpe Ratio (Ann.):      {metrics.sharpe_ratio:.2f}",
            f"  Sortino Ratio (Ann.):     {metrics.sortino_ratio:.2f}",
            f"  Calmar Ratio:             {metrics.calmar_ratio:.2f}",
            f"  Annualized Volatility:    {metrics.annualized_volatility_pct:.2f}%",
            "",
            "  DRAWDOWN & TAIL RISK PROFILE",
            div,
            f"  Maximum Drawdown:         {metrics.max_drawdown_pct:.2f}%",
            f"  Max Drawdown Duration:    {metrics.max_drawdown_duration_bars} bars",
            f"  Value at Risk (VaR 95%):  {metrics.var_95_pct:.2f}%",
            f"  Conditional VaR (CVaR):   {metrics.cvar_95_pct:.2f}%",
            f"  Value at Risk (VaR 99%):  {metrics.var_99_pct:.2f}%",
            "",
            "  TRADE EXECUTION & WIN/LOSS RATIOS",
            div,
            f"  Total Trades Executed:    {metrics.total_trades}",
            f"  Winning Trades / Losing:  {metrics.winning_trades} / {metrics.losing_trades}",
            f"  Win Rate:                 {metrics.win_rate_pct:.2f}%",
            f"  Profit Factor:            {metrics.profit_factor:.2f}",
            f"  Payoff Ratio (Win/Loss):  {metrics.payoff_ratio:.2f}",
            f"  Average Trade Net PnL:    INR {metrics.average_trade_pnl:,.2f}",
            f"  Average Win / Avg Loss:   INR {metrics.average_win:,.2f} / INR {metrics.average_loss:,.2f}",
            f"  Largest Win:              INR {metrics.largest_win:,.2f}",
            f"  Largest Loss:             INR {metrics.largest_loss:,.2f}",
            f"  Trade Expectancy:         INR {metrics.expectancy:,.2f}",
            "",
            "  TRANSACTION FRICTION & REGULATORY AUDIT",
            div,
            f"  Total Statutory Taxes & STT / Brokerage: INR {metrics.total_commissions_and_taxes:,.2f}",
            border,
            "",
        ]
        return "\n".join(lines)
