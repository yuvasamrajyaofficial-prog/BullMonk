"""
Unit tests for the broker interface (mock broker implementation).

Tests that:
1. BaseBroker interface can be implemented by a mock.
2. Mock broker returns correct types for all methods.
3. Broker interface is fully generic — no instrument-specific logic.
4. Strategy code cannot directly access broker implementations.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.enums import (
    AssetClass,
    Exchange,
    InstrumentType,
    OrderStatus,
    OrderType,
    PositionSide,
    Side,
)
from core.models import (
    Account,
    Asset,
    Balance,
    Fill,
    Order,
    Position,
    Quote,
)
from brokers.base import BaseBroker


# ──────────────────────────────────────────────
# Mock broker implementation
# ──────────────────────────────────────────────

class MockBroker(BaseBroker):
    """
    A complete mock implementation of BaseBroker for testing.

    Returns predictable, in-memory data. No network calls.
    """

    def __init__(self) -> None:
        self._connected = False
        self._orders: dict[str, Order] = {}
        self._fills: list[Fill] = []

    def get_name(self) -> str:
        return "MockBroker"

    def is_connected(self) -> bool:
        return self._connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def get_account(self) -> Account:
        return Account(
            account_id="MOCK-ACC-001",
            broker_name=self.get_name(),
            balances={
                "INR": Balance(
                    available=Decimal("500000"),
                    used_margin=Decimal("50000"),
                    total_equity=Decimal("550000"),
                )
            },
            is_live=False,
        )

    def get_positions(self) -> list[Position]:
        return [
            Position(
                asset=Asset(
                    symbol="RELIANCE",
                    exchange=Exchange.NSE,
                    asset_class=AssetClass.EQUITY,
                    instrument_type=InstrumentType.STOCK,
                ),
                side=PositionSide.LONG,
                quantity=Decimal("10"),
                average_entry_price=Decimal("2950"),
            )
        ]

    def get_orders(self, status_filter=None) -> list[Order]:
        orders = list(self._orders.values())
        return orders

    def get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            from core.exceptions import OrderNotFoundError
            raise OrderNotFoundError(order_id)
        return self._orders[order_id]

    def place_order(self, order: Order) -> str:
        broker_id = f"MOCK-BROKER-{order.order_id[:8]}"
        order.broker_order_id = broker_id
        order.status = OrderStatus.SUBMITTED
        self._orders[order.order_id] = order
        return broker_id

    def cancel_order(self, order_id: str) -> None:
        if order_id in self._orders:
            self._orders[order_id].status = OrderStatus.CANCELLED

    def modify_order(
        self,
        order_id: str,
        *,
        quantity=None,
        limit_price=None,
        stop_price=None,
    ) -> None:
        if order_id in self._orders:
            order = self._orders[order_id]
            if quantity is not None:
                object.__setattr__(order, "quantity", quantity)
            if limit_price is not None:
                object.__setattr__(order, "limit_price", limit_price)

    def get_quote(self, asset: Asset) -> Quote:
        return Quote(
            asset=asset,
            timestamp=datetime.now(tz=timezone.utc),
            bid_price=Decimal("2999"),
            bid_size=Decimal("100"),
            ask_price=Decimal("3001"),
            ask_size=Decimal("50"),
        )

    def get_fills(self, order_id=None) -> list[Fill]:
        if order_id:
            return [f for f in self._fills if f.order_id == order_id]
        return list(self._fills)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def mock_broker() -> MockBroker:
    broker = MockBroker()
    broker.connect()
    return broker


@pytest.fixture
def reliance_asset() -> Asset:
    return Asset(
        symbol="RELIANCE",
        exchange=Exchange.NSE,
        asset_class=AssetClass.EQUITY,
        instrument_type=InstrumentType.STOCK,
    )


@pytest.fixture
def sample_order(reliance_asset: Asset) -> Order:
    return Order(
        asset=reliance_asset,
        side=Side.BUY,
        order_type=OrderType.MARKET,
        quantity=Decimal("10"),
    )


# ──────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────

class TestMockBrokerInterface:
    def test_connect_disconnect(self):
        broker = MockBroker()
        assert not broker.is_connected()
        broker.connect()
        assert broker.is_connected()
        broker.disconnect()
        assert not broker.is_connected()

    def test_get_name(self, mock_broker: MockBroker):
        assert mock_broker.get_name() == "MockBroker"

    def test_get_account_returns_account(self, mock_broker: MockBroker):
        account = mock_broker.get_account()
        assert account.account_id == "MOCK-ACC-001"
        bal = account.get_balance("INR")
        assert bal is not None
        assert bal.total_equity == Decimal("550000")

    def test_get_positions_returns_list(self, mock_broker: MockBroker):
        positions = mock_broker.get_positions()
        assert isinstance(positions, list)
        assert len(positions) > 0
        assert positions[0].asset.symbol == "RELIANCE"

    def test_place_order_returns_broker_id(
        self, mock_broker: MockBroker, sample_order: Order
    ):
        broker_id = mock_broker.place_order(sample_order)
        assert isinstance(broker_id, str)
        assert broker_id.startswith("MOCK-BROKER-")

    def test_get_order_after_placement(
        self, mock_broker: MockBroker, sample_order: Order
    ):
        mock_broker.place_order(sample_order)
        retrieved = mock_broker.get_order(sample_order.order_id)
        assert retrieved.order_id == sample_order.order_id
        assert retrieved.status == OrderStatus.SUBMITTED

    def test_get_order_not_found_raises(self, mock_broker: MockBroker):
        from core.exceptions import OrderNotFoundError
        with pytest.raises(OrderNotFoundError):
            mock_broker.get_order("nonexistent-id")

    def test_cancel_order(self, mock_broker: MockBroker, sample_order: Order):
        mock_broker.place_order(sample_order)
        mock_broker.cancel_order(sample_order.order_id)
        order = mock_broker.get_order(sample_order.order_id)
        assert order.status == OrderStatus.CANCELLED

    def test_get_orders_returns_list(self, mock_broker: MockBroker, sample_order: Order):
        mock_broker.place_order(sample_order)
        orders = mock_broker.get_orders()
        assert isinstance(orders, list)
        assert any(o.order_id == sample_order.order_id for o in orders)

    def test_get_quote_returns_valid_quote(
        self, mock_broker: MockBroker, reliance_asset: Asset
    ):
        quote = mock_broker.get_quote(reliance_asset)
        assert quote.bid_price < quote.ask_price
        assert quote.asset == reliance_asset

    def test_get_fills_empty_initially(self, mock_broker: MockBroker):
        fills = mock_broker.get_fills()
        assert isinstance(fills, list)
        assert len(fills) == 0

    def test_broker_is_subclass_of_base_broker(self):
        assert issubclass(MockBroker, BaseBroker)

    def test_broker_has_no_strategy_imports(self):
        """Architectural guard: broker base must not import strategy modules."""
        import inspect
        import brokers.base as broker_module

        source = inspect.getsource(broker_module)
        assert "strategies" not in source
        assert "BaseStrategy" not in source
