"""Unit tests for SimulatedMatchingEngine."""

from datetime import datetime, timezone
from decimal import Decimal
import pytest

from backtesting.costs import ZeroCostModel, ZeroSlippageModel
from backtesting.matching_engine import SimulatedMatchingEngine
from core.enums import OrderType, Side, Timeframe
from core.models import OHLCVBar, Order
from data.nifty import create_nifty_index


@pytest.fixture
def sample_bar() -> OHLCVBar:
    return OHLCVBar(
        asset=create_nifty_index(),
        timeframe=Timeframe.M15,
        timestamp=datetime(2025, 1, 15, 9, 15, tzinfo=timezone.utc),
        open=Decimal("24000.00"),
        high=Decimal("24100.00"),
        low=Decimal("23950.00"),
        close=Decimal("24050.00"),
        volume=50000,
    )


class TestSimulatedMatchingEngine:
    def test_market_order_fill_on_open(self, sample_bar: OHLCVBar):
        engine = SimulatedMatchingEngine(
            cost_model=ZeroCostModel(),
            slippage_model=ZeroSlippageModel(),
            fill_on_next_open=True,
        )
        order = Order(
            order_id="ORD-1",
            asset=sample_bar.asset,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("50"),
        )
        engine.submit_order(order)
        fills = engine.process_bar(sample_bar)

        assert len(fills) == 1
        assert fills[0].order_id == "ORD-1"
        assert fills[0].price == Decimal("24000.00")  # Filled at bar Open
        assert fills[0].quantity == Decimal("50")

    def test_buy_limit_order_fills_when_low_crosses(self, sample_bar: OHLCVBar):
        engine = SimulatedMatchingEngine(cost_model=ZeroCostModel(), slippage_model=ZeroSlippageModel())
        # Limit at 23980 is between high 24100 and low 23950
        order = Order(
            order_id="ORD-L1",
            asset=sample_bar.asset,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            limit_price=Decimal("23980.00"),
            quantity=Decimal("25"),
        )
        engine.submit_order(order)
        fills = engine.process_bar(sample_bar)

        assert len(fills) == 1
        assert fills[0].price == Decimal("23980.00")

    def test_buy_limit_order_does_not_fill_when_low_higher(self, sample_bar: OHLCVBar):
        engine = SimulatedMatchingEngine(cost_model=ZeroCostModel(), slippage_model=ZeroSlippageModel())
        # Limit at 23900 is below bar low (23950) -> Should NOT fill
        order = Order(
            order_id="ORD-L2",
            asset=sample_bar.asset,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            limit_price=Decimal("23900.00"),
            quantity=Decimal("25"),
        )
        engine.submit_order(order)
        fills = engine.process_bar(sample_bar)

        assert len(fills) == 0
        assert engine.open_orders_count == 1

    def test_sell_limit_order_fills_when_high_crosses(self, sample_bar: OHLCVBar):
        engine = SimulatedMatchingEngine(cost_model=ZeroCostModel(), slippage_model=ZeroSlippageModel())
        # Limit sell at 24080 is below bar high (24100) -> Should fill
        order = Order(
            order_id="ORD-L3",
            asset=sample_bar.asset,
            side=Side.SELL,
            order_type=OrderType.LIMIT,
            limit_price=Decimal("24080.00"),
            quantity=Decimal("25"),
        )
        engine.submit_order(order)
        fills = engine.process_bar(sample_bar)

        assert len(fills) == 1
        assert fills[0].price == Decimal("24080.00")

    def test_cancel_order(self, sample_bar: OHLCVBar):
        engine = SimulatedMatchingEngine()
        order = Order(
            order_id="ORD-CANCEL",
            asset=sample_bar.asset,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            limit_price=Decimal("23500.00"),
            quantity=Decimal("10"),
        )
        engine.submit_order(order)
        assert engine.open_orders_count == 1

        cancelled = engine.cancel_order("ORD-CANCEL")
        assert cancelled is True
        assert engine.open_orders_count == 0
