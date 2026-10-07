"""
Unit tests for core enumerations.

Tests that:
1. All enum classes can be instantiated.
2. Enum values are correct strings.
3. Enum membership checks work.
4. String-based enum comparison works.
"""

import pytest

from core.enums import (
    AssetClass,
    EventType,
    Exchange,
    InstrumentType,
    MarketState,
    OptionStyle,
    OptionType,
    OrderStatus,
    OrderType,
    PositionSide,
    ProductType,
    RiskDecisionType,
    Side,
    SignalType,
    StrategyState,
    Timeframe,
    TimeInForce,
)


class TestAssetClass:
    def test_all_members_exist(self):
        assert AssetClass.EQUITY == "EQUITY"
        assert AssetClass.FUTURES == "FUTURES"
        assert AssetClass.OPTIONS == "OPTIONS"
        assert AssetClass.FOREX == "FOREX"
        assert AssetClass.CRYPTO == "CRYPTO"
        assert AssetClass.COMMODITY == "COMMODITY"
        assert AssetClass.BOND == "BOND"
        assert AssetClass.ETF == "ETF"

    def test_string_comparison(self):
        assert AssetClass.EQUITY == "EQUITY"

    def test_membership(self):
        assert AssetClass.CRYPTO in AssetClass


class TestExchange:
    def test_indian_exchanges(self):
        assert Exchange.NSE == "NSE"
        assert Exchange.BSE == "BSE"
        assert Exchange.NFO == "NFO"
        assert Exchange.MCX == "MCX"

    def test_crypto_exchanges(self):
        assert Exchange.BINANCE == "BINANCE"
        assert Exchange.COINBASE == "COINBASE"

    def test_global_equity(self):
        assert Exchange.NYSE == "NYSE"
        assert Exchange.NASDAQ == "NASDAQ"


class TestSide:
    def test_buy_sell(self):
        assert Side.BUY == "BUY"
        assert Side.SELL == "SELL"

    def test_exactly_two_members(self):
        assert len(Side) == 2


class TestOrderType:
    def test_all_types(self):
        assert OrderType.MARKET == "MARKET"
        assert OrderType.LIMIT == "LIMIT"
        assert OrderType.STOP == "STOP"
        assert OrderType.STOP_LIMIT == "STOP_LIMIT"
        assert OrderType.TRAILING_STOP == "TRAILING_STOP"


class TestOrderStatus:
    def test_all_statuses(self):
        expected = {
            "PENDING", "SUBMITTED", "OPEN", "PARTIALLY_FILLED",
            "FILLED", "CANCELLED", "REJECTED", "EXPIRED",
            "PENDING_CANCEL", "PENDING_MODIFY",
        }
        actual = {s.value for s in OrderStatus}
        assert expected == actual


class TestTimeframe:
    def test_minute_bars(self):
        assert Timeframe.M1 == "1m"
        assert Timeframe.M5 == "5m"
        assert Timeframe.M15 == "15m"

    def test_daily_bar(self):
        assert Timeframe.D1 == "1d"

    def test_weekly_bar(self):
        assert Timeframe.W1 == "1w"


class TestSignalType:
    def test_all_signal_types(self):
        assert SignalType.ENTER_LONG == "ENTER_LONG"
        assert SignalType.ENTER_SHORT == "ENTER_SHORT"
        assert SignalType.EXIT_LONG == "EXIT_LONG"
        assert SignalType.EXIT_SHORT == "EXIT_SHORT"
        assert SignalType.NO_SIGNAL == "NO_SIGNAL"
        assert SignalType.CLOSE_ALL == "CLOSE_ALL"


class TestOptionType:
    def test_call_put(self):
        assert OptionType.CALL == "CE"
        assert OptionType.PUT == "PE"


class TestProductType:
    def test_indian_product_types(self):
        assert ProductType.CNC == "CNC"
        assert ProductType.MIS == "MIS"
        assert ProductType.NRML == "NRML"


class TestEventType:
    def test_market_data_events(self):
        assert EventType.BAR == "BAR"
        assert EventType.TICK == "TICK"
        assert EventType.QUOTE == "QUOTE"

    def test_order_events(self):
        assert EventType.ORDER_FILLED == "ORDER_FILLED"
        assert EventType.ORDER_REJECTED == "ORDER_REJECTED"

    def test_risk_events(self):
        assert EventType.RISK_BREACH == "RISK_BREACH"
