"""Integration tests for EventDrivenBacktestEngine and Strategy Library."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from backtesting.costs import IndianMarketCostModel, ZeroCostModel, ZeroSlippageModel
from backtesting.event_engine import EventDrivenBacktestEngine
from core.enums import Timeframe
from data.nifty import create_nifty_index
from data.providers.synthetic_provider import SyntheticHistoricalProvider
from strategies.library import BollingerReversionStrategy, DualEMAStrategy, OpeningRangeBreakoutStrategy


@pytest.fixture
def data_provider() -> SyntheticHistoricalProvider:
    return SyntheticHistoricalProvider(seed=123, volatility=0.15)


class TestBacktestEngineIntegration:
    def test_dual_ema_backtest_runs_cleanly(self, data_provider: SyntheticHistoricalProvider):
        strategy = DualEMAStrategy(fast_period=5, slow_period=15, trade_quantity=Decimal("50"))
        engine = EventDrivenBacktestEngine(
            data_provider=data_provider,
            initial_capital=Decimal("1000000.00"),
            cost_model=IndianMarketCostModel(),
            fill_on_next_open=True,
        )
        asset = create_nifty_index()
        start = datetime(2025, 1, 1, 3, 45, tzinfo=timezone.utc)
        end = datetime(2025, 1, 10, 10, 0, tzinfo=timezone.utc)

        result = engine.run(
            strategy=strategy,
            asset=asset,
            timeframe=Timeframe.M15,
            start=start,
            end=end,
        )

        assert result.bars_processed > 0
        assert result.signals_generated >= 0
        assert result.metrics is not None
        assert result.metrics.initial_capital == Decimal("1000000.00")
        assert len(result.snapshots) == result.bars_processed

    def test_opening_range_breakout_strategy_backtest(self, data_provider: SyntheticHistoricalProvider):
        strategy = OpeningRangeBreakoutStrategy(orb_minutes=30, trade_quantity=Decimal("50"))
        engine = EventDrivenBacktestEngine(
            data_provider=data_provider,
            initial_capital=Decimal("1000000.00"),
            cost_model=ZeroCostModel(),
            slippage_model=ZeroSlippageModel(),
        )
        asset = create_nifty_index()
        start = datetime(2025, 1, 1, 3, 45, tzinfo=timezone.utc)
        end = datetime(2025, 1, 5, 10, 0, tzinfo=timezone.utc)

        result = engine.run(
            strategy=strategy,
            asset=asset,
            timeframe=Timeframe.M5,
            start=start,
            end=end,
        )

        assert result.bars_processed > 0
        assert result.metrics is not None

    def test_bollinger_reversion_strategy_backtest(self, data_provider: SyntheticHistoricalProvider):
        strategy = BollingerReversionStrategy(period=15, num_std=1.8, trade_quantity=Decimal("50"))
        engine = EventDrivenBacktestEngine(
            data_provider=data_provider,
            initial_capital=Decimal("1000000.00"),
        )
        asset = create_nifty_index()
        start = datetime(2025, 1, 1, 3, 45, tzinfo=timezone.utc)
        end = datetime(2025, 1, 10, 10, 0, tzinfo=timezone.utc)

        result = engine.run(
            strategy=strategy,
            asset=asset,
            timeframe=Timeframe.M15,
            start=start,
            end=end,
        )

        assert result.bars_processed > 0
        assert result.metrics is not None
