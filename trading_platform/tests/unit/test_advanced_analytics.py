"""Unit tests for AdvancedAnalyticsEngine."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from analytics.advanced_metrics import AdvancedAnalyticsEngine
from core.enums import Side
from core.models import PortfolioSnapshot, Trade
from data.nifty import create_nifty_index


class TestAdvancedAnalyticsEngine:
    def test_metrics_on_empty_trades(self):
        engine = AdvancedAnalyticsEngine()
        metrics = engine.compute_metrics(
            trades=[],
            equity_snapshots=[],
            initial_capital=Decimal("1000000.00"),
        )
        assert metrics.total_trades == 0
        assert metrics.win_rate_pct == 0.0
        assert metrics.profit_factor == 0.0
        assert metrics.total_net_pnl == Decimal("0.00")

    def test_metrics_with_winning_and_losing_trades(self):
        engine = AdvancedAnalyticsEngine()
        asset = create_nifty_index()
        t1 = datetime(2025, 1, 1, 9, 15, tzinfo=timezone.utc)
        t2 = datetime(2025, 1, 1, 10, 0, tzinfo=timezone.utc)

        trades = [
            Trade(
                trade_id="T1",
                asset=asset,
                side=Side.BUY,
                entry_time=t1,
                exit_time=t2,
                entry_price=Decimal("100"),
                exit_price=Decimal("110"),
                quantity=Decimal("10"),
                gross_pnl=Decimal("100"),
                commission=Decimal("10"),
                net_pnl=Decimal("90"),  # Winner
            ),
            Trade(
                trade_id="T2",
                asset=asset,
                side=Side.BUY,
                entry_time=t1,
                exit_time=t2,
                entry_price=Decimal("100"),
                exit_price=Decimal("95"),
                quantity=Decimal("10"),
                gross_pnl=Decimal("-50"),
                commission=Decimal("10"),
                net_pnl=Decimal("-60"),  # Loser
            ),
        ]

        snapshots = [
            PortfolioSnapshot(
                timestamp=t1,
                account_id="ACC1",
                positions=[],
                total_equity=Decimal("1000000.00"),
                total_unrealized_pnl=Decimal("0"),
                total_realized_pnl=Decimal("0"),
                cash_balance=Decimal("1000000.00"),
            ),
            PortfolioSnapshot(
                timestamp=t2,
                account_id="ACC1",
                positions=[],
                total_equity=Decimal("1000030.00"),
                total_unrealized_pnl=Decimal("0"),
                total_realized_pnl=Decimal("30"),
                cash_balance=Decimal("1000030.00"),
            ),
        ]

        metrics = engine.compute_metrics(
            trades=trades,
            equity_snapshots=snapshots,
            initial_capital=Decimal("1000000.00"),
        )

        assert metrics.total_trades == 2
        assert metrics.winning_trades == 1
        assert metrics.losing_trades == 1
        assert metrics.win_rate_pct == 50.0
        assert metrics.profit_factor == 1.5  # 90 / 60 = 1.5
        assert metrics.total_net_pnl == Decimal("30.00")
