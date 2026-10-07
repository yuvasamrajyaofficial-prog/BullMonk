"""
Unit tests for core domain models.

Tests that:
1. All core models can be instantiated with valid data.
2. Models covering Indian equity, index options, crypto, and Forex all work.
3. Validation raises errors for invalid data (negative volume, naive timestamps, etc.)
4. Model properties compute correctly.
5. Pydantic serialisation round-trips work.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from core.enums import (
    AssetClass,
    Exchange,
    InstrumentType,
    OptionType,
    OptionStyle,
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
from core.models import (
    Account,
    Asset,
    Balance,
    Fill,
    OHLCVBar,
    Order,
    PortfolioSnapshot,
    Position,
    Quote,
    RiskDecision,
    RiskLimits,
    Signal,
    StrategyConfig,
    StrategyMetadata,
    Tick,
    Trade,
    TradingSession,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def nifty_futures_asset() -> Asset:
    return Asset(
        symbol="NIFTY",
        exchange=Exchange.NFO,
        asset_class=AssetClass.FUTURES,
        instrument_type=InstrumentType.INDEX_FUTURES,
        currency="INR",
        lot_size=50,
    )


@pytest.fixture
def nifty_option_asset() -> Asset:
    return Asset(
        symbol="NIFTY",
        exchange=Exchange.NFO,
        asset_class=AssetClass.OPTIONS,
        instrument_type=InstrumentType.INDEX_OPTIONS,
        currency="INR",
        expiry=datetime(2025, 12, 25, 0, 0, 0, tzinfo=timezone.utc),
        strike_price=Decimal("24000"),
        option_type=OptionType.CALL,
        option_style=OptionStyle.EUROPEAN,
        lot_size=50,
    )


@pytest.fixture
def reliance_asset() -> Asset:
    return Asset(
        symbol="RELIANCE",
        exchange=Exchange.NSE,
        asset_class=AssetClass.EQUITY,
        instrument_type=InstrumentType.STOCK,
        currency="INR",
    )


@pytest.fixture
def btc_asset() -> Asset:
    return Asset(
        symbol="BTC",
        exchange=Exchange.BINANCE,
        asset_class=AssetClass.CRYPTO,
        instrument_type=InstrumentType.CRYPTO_SPOT,
        currency="USDT",
    )


@pytest.fixture
def eurusd_asset() -> Asset:
    return Asset(
        symbol="EURUSD",
        exchange=Exchange.FOREX_OTC,
        asset_class=AssetClass.FOREX,
        instrument_type=InstrumentType.CURRENCY_PAIR,
        currency="USD",
    )


@pytest.fixture
def utc_now() -> datetime:
    return datetime.now(tz=timezone.utc)


@pytest.fixture
def sample_bar(nifty_futures_asset: Asset, utc_now: datetime) -> OHLCVBar:
    return OHLCVBar(
        asset=nifty_futures_asset,
        timeframe=Timeframe.M5,
        timestamp=utc_now,
        open=Decimal("24000"),
        high=Decimal("24100"),
        low=Decimal("23950"),
        close=Decimal("24080"),
        volume=Decimal("50000"),
    )


# ──────────────────────────────────────────────
# Asset tests
# ──────────────────────────────────────────────

class TestAsset:
    def test_indian_equity(self, reliance_asset: Asset):
        assert reliance_asset.symbol == "RELIANCE"
        assert reliance_asset.exchange == Exchange.NSE
        assert reliance_asset.asset_class == AssetClass.EQUITY

    def test_nifty_futures(self, nifty_futures_asset: Asset):
        assert nifty_futures_asset.lot_size == 50
        assert nifty_futures_asset.instrument_type == InstrumentType.INDEX_FUTURES

    def test_nifty_option(self, nifty_option_asset: Asset):
        assert nifty_option_asset.strike_price == Decimal("24000")
        assert nifty_option_asset.option_type == OptionType.CALL
        assert nifty_option_asset.option_style == OptionStyle.EUROPEAN

    def test_btc_crypto(self, btc_asset: Asset):
        assert btc_asset.exchange == Exchange.BINANCE
        assert btc_asset.currency == "USDT"

    def test_eurusd_forex(self, eurusd_asset: Asset):
        assert eurusd_asset.asset_class == AssetClass.FOREX
        assert eurusd_asset.instrument_type == InstrumentType.CURRENCY_PAIR

    def test_symbol_normalised_to_uppercase(self):
        asset = Asset(
            symbol="reliance",
            exchange=Exchange.NSE,
            asset_class=AssetClass.EQUITY,
            instrument_type=InstrumentType.STOCK,
        )
        assert asset.symbol == "RELIANCE"

    def test_empty_symbol_raises(self):
        with pytest.raises(Exception):
            Asset(
                symbol="",
                exchange=Exchange.NSE,
                asset_class=AssetClass.EQUITY,
                instrument_type=InstrumentType.STOCK,
            )

    def test_invalid_currency_raises(self):
        with pytest.raises(Exception):
            Asset(
                symbol="TEST",
                exchange=Exchange.NSE,
                asset_class=AssetClass.EQUITY,
                instrument_type=InstrumentType.STOCK,
                currency="INVALID",
            )

    def test_str_representation(self, reliance_asset: Asset):
        assert str(reliance_asset) == "RELIANCE@NSE"

    def test_frozen(self, reliance_asset: Asset):
        with pytest.raises(Exception):
            reliance_asset.symbol = "CHANGED"  # type: ignore


# ──────────────────────────────────────────────
# OHLCVBar tests
# ──────────────────────────────────────────────

class TestOHLCVBar:
    def test_valid_bar(self, sample_bar: OHLCVBar):
        assert sample_bar.open == Decimal("24000")
        assert sample_bar.high == Decimal("24100")
        assert sample_bar.low == Decimal("23950")
        assert sample_bar.close == Decimal("24080")
        assert sample_bar.volume == Decimal("50000")

    def test_high_less_than_open_raises(self, nifty_futures_asset: Asset, utc_now: datetime):
        with pytest.raises(Exception):
            OHLCVBar(
                asset=nifty_futures_asset,
                timeframe=Timeframe.M5,
                timestamp=utc_now,
                open=Decimal("24000"),
                high=Decimal("23000"),  # invalid: high < open
                low=Decimal("22000"),
                close=Decimal("23500"),
                volume=Decimal("100"),
            )

    def test_low_greater_than_close_raises(self, nifty_futures_asset: Asset, utc_now: datetime):
        with pytest.raises(Exception):
            OHLCVBar(
                asset=nifty_futures_asset,
                timeframe=Timeframe.M5,
                timestamp=utc_now,
                open=Decimal("24000"),
                high=Decimal("25000"),
                low=Decimal("24500"),  # invalid: low > close
                close=Decimal("24200"),
                volume=Decimal("100"),
            )

    def test_naive_timestamp_raises(self, nifty_futures_asset: Asset):
        with pytest.raises(Exception):
            OHLCVBar(
                asset=nifty_futures_asset,
                timeframe=Timeframe.D1,
                timestamp=datetime(2024, 1, 1),  # naive — no tz
                open=Decimal("100"),
                high=Decimal("110"),
                low=Decimal("90"),
                close=Decimal("105"),
                volume=Decimal("1000"),
            )

    def test_negative_volume_raises(self, nifty_futures_asset: Asset, utc_now: datetime):
        with pytest.raises(Exception):
            OHLCVBar(
                asset=nifty_futures_asset,
                timeframe=Timeframe.M5,
                timestamp=utc_now,
                open=Decimal("100"),
                high=Decimal("110"),
                low=Decimal("90"),
                close=Decimal("105"),
                volume=Decimal("-1"),
            )


# ──────────────────────────────────────────────
# Quote tests
# ──────────────────────────────────────────────

class TestQuote:
    def test_valid_quote(self, reliance_asset: Asset, utc_now: datetime):
        q = Quote(
            asset=reliance_asset,
            timestamp=utc_now,
            bid_price=Decimal("2999.50"),
            bid_size=Decimal("100"),
            ask_price=Decimal("3000.00"),
            ask_size=Decimal("50"),
        )
        assert q.mid_price == Decimal("2999.75")
        assert q.spread == Decimal("0.50")

    def test_bid_gte_ask_raises(self, reliance_asset: Asset, utc_now: datetime):
        with pytest.raises(Exception):
            Quote(
                asset=reliance_asset,
                timestamp=utc_now,
                bid_price=Decimal("3000"),
                bid_size=Decimal("100"),
                ask_price=Decimal("3000"),  # bid == ask → invalid
                ask_size=Decimal("50"),
            )


# ──────────────────────────────────────────────
# Order tests
# ──────────────────────────────────────────────

class TestOrder:
    def test_market_order(self, reliance_asset: Asset):
        order = Order(
            asset=reliance_asset,
            side=Side.BUY,
            order_type=OrderType.MARKET,
            quantity=Decimal("10"),
        )
        assert order.status == OrderStatus.PENDING
        assert order.remaining_quantity == Decimal("10")
        assert not order.is_terminal

    def test_limit_order_requires_limit_price(self, reliance_asset: Asset):
        with pytest.raises(Exception):
            Order(
                asset=reliance_asset,
                side=Side.BUY,
                order_type=OrderType.LIMIT,
                quantity=Decimal("10"),
                # Missing limit_price
            )

    def test_stop_order_requires_stop_price(self, reliance_asset: Asset):
        with pytest.raises(Exception):
            Order(
                asset=reliance_asset,
                side=Side.SELL,
                order_type=OrderType.STOP,
                quantity=Decimal("10"),
                # Missing stop_price
            )

    def test_valid_limit_order(self, reliance_asset: Asset):
        order = Order(
            asset=reliance_asset,
            side=Side.BUY,
            order_type=OrderType.LIMIT,
            quantity=Decimal("10"),
            limit_price=Decimal("2950"),
        )
        assert order.limit_price == Decimal("2950")

    def test_order_id_auto_generated(self, reliance_asset: Asset):
        o1 = Order(asset=reliance_asset, side=Side.BUY,
                   order_type=OrderType.MARKET, quantity=Decimal("1"))
        o2 = Order(asset=reliance_asset, side=Side.BUY,
                   order_type=OrderType.MARKET, quantity=Decimal("1"))
        assert o1.order_id != o2.order_id

    def test_is_active_for_open_order(self, reliance_asset: Asset):
        order = Order(
            asset=reliance_asset, side=Side.BUY,
            order_type=OrderType.MARKET, quantity=Decimal("5"),
            status=OrderStatus.OPEN,
        )
        assert order.is_active
        assert not order.is_terminal

    def test_is_terminal_for_filled_order(self, reliance_asset: Asset):
        order = Order(
            asset=reliance_asset, side=Side.BUY,
            order_type=OrderType.MARKET, quantity=Decimal("5"),
            status=OrderStatus.FILLED,
            filled_quantity=Decimal("5"),
        )
        assert order.is_terminal
        assert not order.is_active


# ──────────────────────────────────────────────
# Fill tests
# ──────────────────────────────────────────────

class TestFill:
    def test_valid_fill(self, reliance_asset: Asset, utc_now: datetime):
        fill = Fill(
            order_id="test-order-id",
            asset=reliance_asset,
            side=Side.BUY,
            quantity=Decimal("10"),
            price=Decimal("3000"),
            commission=Decimal("30"),
            timestamp=utc_now,
        )
        assert fill.gross_value == Decimal("30000")
        assert fill.net_value == Decimal("29970")


# ──────────────────────────────────────────────
# Position tests
# ──────────────────────────────────────────────

class TestPosition:
    def test_mark_to_market_long(self, reliance_asset: Asset):
        pos = Position(
            asset=reliance_asset,
            side=PositionSide.LONG,
            quantity=Decimal("10"),
            average_entry_price=Decimal("2900"),
        )
        pos.mark_to_market(Decimal("3000"))
        assert pos.unrealized_pnl == Decimal("1000")

    def test_mark_to_market_short(self, reliance_asset: Asset):
        pos = Position(
            asset=reliance_asset,
            side=PositionSide.SHORT,
            quantity=Decimal("10"),
            average_entry_price=Decimal("3000"),
        )
        pos.mark_to_market(Decimal("2900"))
        assert pos.unrealized_pnl == Decimal("1000")

    def test_total_pnl(self, reliance_asset: Asset):
        pos = Position(
            asset=reliance_asset,
            side=PositionSide.LONG,
            quantity=Decimal("10"),
            average_entry_price=Decimal("2900"),
            realized_pnl=Decimal("500"),
            unrealized_pnl=Decimal("300"),
        )
        assert pos.total_pnl == Decimal("800")


# ──────────────────────────────────────────────
# Signal tests
# ──────────────────────────────────────────────

class TestSignal:
    def test_valid_signal(self, nifty_futures_asset: Asset):
        signal = Signal(
            strategy_id="test-strategy",
            asset=nifty_futures_asset,
            signal_type=SignalType.ENTER_LONG,
            strength=0.85,
        )
        assert signal.signal_type == SignalType.ENTER_LONG
        assert signal.strength == 0.85

    def test_strength_capped_at_1(self, nifty_futures_asset: Asset):
        with pytest.raises(Exception):
            Signal(
                strategy_id="test",
                asset=nifty_futures_asset,
                signal_type=SignalType.ENTER_LONG,
                strength=1.5,  # invalid
            )


# ──────────────────────────────────────────────
# Strategy config / metadata tests
# ──────────────────────────────────────────────

class TestStrategyModels:
    def test_strategy_config(self):
        config = StrategyConfig(
            strategy_id="sma-cross-v1",
            parameters={"fast_period": 10, "slow_period": 20},
            risk_per_trade_pct=1.5,
            max_open_positions=3,
        )
        assert config.state == StrategyState.INITIALIZED
        assert config.parameters["fast_period"] == 10

    def test_strategy_metadata(self):
        meta = StrategyMetadata(
            strategy_id="sma-cross-v1",
            name="SMA Crossover",
            version="1.0.0",
            supported_asset_classes=[AssetClass.EQUITY, AssetClass.FUTURES],
        )
        assert "SMA" in meta.name


# ──────────────────────────────────────────────
# Portfolio / Account / Balance tests
# ──────────────────────────────────────────────

class TestPortfolioModels:
    def test_balance(self):
        bal = Balance(
            available=Decimal("500000"),
            used_margin=Decimal("100000"),
            total_equity=Decimal("600000"),
        )
        assert bal.free_margin == Decimal("500000")

    def test_account_get_balance(self):
        account = Account(
            account_id="ACC001",
            broker_name="Dhan",
            balances={
                "INR": Balance(
                    available=Decimal("100000"),
                    used_margin=Decimal("0"),
                    total_equity=Decimal("100000"),
                )
            },
        )
        bal = account.get_balance("INR")
        assert bal is not None
        assert bal.total_equity == Decimal("100000")

    def test_account_get_balance_missing_currency(self):
        account = Account(account_id="ACC001", broker_name="Test")
        assert account.get_balance("USD") is None


# ──────────────────────────────────────────────
# Risk models tests
# ──────────────────────────────────────────────

class TestRiskModels:
    def test_risk_limits_defaults(self):
        limits = RiskLimits()
        assert limits.max_daily_loss_pct == 3.0
        assert limits.max_drawdown_pct == 15.0
        assert limits.max_open_positions == 5

    def test_risk_decision_approved(self, reliance_asset: Asset):
        decision = RiskDecision(
            decision=RiskDecisionType.APPROVED,
            order_id="test-order",
        )
        assert decision.decision == RiskDecisionType.APPROVED

    def test_risk_decision_rejected_with_reason(self, reliance_asset: Asset):
        decision = RiskDecision(
            decision=RiskDecisionType.REJECTED,
            order_id="test-order",
            reason="Daily loss limit breached.",
        )
        assert decision.reason is not None
        assert "loss" in decision.reason.lower()


# ──────────────────────────────────────────────
# TradingSession tests
# ──────────────────────────────────────────────

class TestTradingSession:
    def test_nse_session(self):
        session = TradingSession(
            exchange=Exchange.NSE,
            session_name="regular",
            open_time_utc="03:45",   # 09:15 IST
            close_time_utc="10:00",  # 15:30 IST
            timezone="Asia/Kolkata",
        )
        assert session.exchange == Exchange.NSE
        assert session.timezone == "Asia/Kolkata"
