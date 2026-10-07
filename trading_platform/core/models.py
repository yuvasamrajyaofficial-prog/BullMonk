"""
Core domain models for the trading platform.

All models are broker-agnostic Pydantic BaseModel instances.
They form the universal vocabulary of the system —
the same types represent NIFTY options, BTC futures, EURUSD, etc.

Design decisions:
- Pydantic v2 used for validation, serialisation, and clear field contracts.
- datetime fields are always timezone-aware (UTC preferred internally).
- Optional fields with None defaults represent data that may not be available
  for all asset classes (e.g. strike_price is None for stocks).
- Immutable where it makes sense (frozen=True) to prevent accidental mutation.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator, model_validator

from core.enums import (
    AssetClass,
    DataSource,
    Exchange,
    InstrumentType,
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


def _utc_now() -> datetime:
    """Return current UTC datetime (timezone-aware)."""
    return datetime.now(tz=timezone.utc)


def _new_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


# ══════════════════════════════════════════════════════════════════════════════
# MARKET / INSTRUMENT MODELS
# ══════════════════════════════════════════════════════════════════════════════

class Asset(BaseModel):
    """
    Uniquely identifies a tradable instrument across all asset classes.

    The combination (symbol, exchange) must be unique within the platform.
    Optional derivative fields are None for non-derivative instruments.
    """

    model_config = {"frozen": True}

    symbol: str = Field(..., description="Canonical ticker symbol (e.g. RELIANCE, NIFTY, BTC)")
    exchange: Exchange = Field(..., description="Exchange or venue where the asset trades")
    asset_class: AssetClass = Field(..., description="Broad classification of the asset")
    instrument_type: InstrumentType = Field(..., description="Fine-grained instrument type")
    currency: str = Field(default="INR", description="Settlement currency ISO-4217 code")

    # Derivative-specific (optional)
    expiry: Optional[datetime] = Field(
        default=None, description="Contract expiry (UTC); None for non-expiring instruments"
    )
    strike_price: Optional[Decimal] = Field(
        default=None, description="Option strike price; None for non-option instruments"
    )
    option_type: Optional[OptionType] = Field(
        default=None, description="CE or PE; None for non-option instruments"
    )
    option_style: Optional[OptionStyle] = Field(
        default=None, description="European / American; None for non-option instruments"
    )
    lot_size: Optional[int] = Field(
        default=None, description="Contract lot size (F&O / crypto futures)"
    )
    tick_size: Optional[Decimal] = Field(
        default=None, description="Minimum price increment"
    )

    @field_validator("symbol")
    @classmethod
    def symbol_must_be_non_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("symbol must not be empty or whitespace")
        return v.upper().strip()

    @field_validator("currency")
    @classmethod
    def currency_must_be_valid(cls, v: str) -> str:
        clean = v.strip().upper()
        if not (3 <= len(clean) <= 5) or not clean.isalnum():
            raise ValueError("currency must be a valid 3-5 character currency code (e.g. INR, USD, USDT)")
        return clean

    def __str__(self) -> str:
        return f"{self.symbol}@{self.exchange.value}"


class TradingSession(BaseModel):
    """Represents a market trading session window."""

    model_config = {"frozen": True}

    exchange: Exchange
    session_name: str = Field(..., description="e.g. 'regular', 'pre-open', 'commodity-evening'")
    open_time_utc: str = Field(..., description="HH:MM session open in UTC")
    close_time_utc: str = Field(..., description="HH:MM session close in UTC")
    timezone: str = Field(..., description="Exchange local timezone string, e.g. 'Asia/Kolkata'")


# ══════════════════════════════════════════════════════════════════════════════
# MARKET DATA MODELS
# ══════════════════════════════════════════════════════════════════════════════

class OHLCVBar(BaseModel):
    """
    A single OHLCV (Open/High/Low/Close/Volume) candlestick bar.

    Immutable after creation. All price values use Decimal for precision.
    """

    model_config = {"frozen": True}

    asset: Asset
    timeframe: Timeframe
    timestamp: datetime = Field(..., description="Bar open timestamp (UTC, timezone-aware)")
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    open_interest: Optional[Decimal] = Field(
        default=None, description="Open interest (derivatives)"
    )
    data_source: DataSource = Field(
        default=DataSource.REAL, description="Data provenance (REAL, SYNTHETIC, BACKTEST_SIMULATED)"
    )

    @property
    def is_synthetic(self) -> bool:
        """Return True if this bar represents synthetic/simulated research data."""
        return self.data_source == DataSource.SYNTHETIC

    @model_validator(mode="after")
    def validate_ohlcv_consistency(self) -> "OHLCVBar":
        if self.high < self.open:
            raise ValueError(f"high ({self.high}) < open ({self.open})")
        if self.high < self.close:
            raise ValueError(f"high ({self.high}) < close ({self.close})")
        if self.low > self.open:
            raise ValueError(f"low ({self.low}) > open ({self.open})")
        if self.low > self.close:
            raise ValueError(f"low ({self.low}) > close ({self.close})")
        if self.volume < 0:
            raise ValueError("volume must not be negative")
        if self.timestamp.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return self


class Tick(BaseModel):
    """A single trade tick — last traded price and volume at a moment in time."""

    model_config = {"frozen": True}

    asset: Asset
    timestamp: datetime
    last_price: Decimal
    last_quantity: Decimal
    total_volume: Optional[Decimal] = None
    open_interest: Optional[Decimal] = None

    @field_validator("timestamp")
    @classmethod
    def must_be_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v


class Quote(BaseModel):
    """Best bid/ask quote at a given moment."""

    model_config = {"frozen": True}

    asset: Asset
    timestamp: datetime
    bid_price: Decimal
    bid_size: Decimal
    ask_price: Decimal
    ask_size: Decimal

    @field_validator("timestamp")
    @classmethod
    def must_be_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v

    @model_validator(mode="after")
    def bid_must_be_less_than_ask(self) -> "Quote":
        if self.bid_price >= self.ask_price:
            raise ValueError(
                f"bid_price ({self.bid_price}) must be < ask_price ({self.ask_price})"
            )
        return self

    @property
    def mid_price(self) -> Decimal:
        return (self.bid_price + self.ask_price) / Decimal("2")

    @property
    def spread(self) -> Decimal:
        return self.ask_price - self.bid_price


class MarketDataSnapshot(BaseModel):
    """A composite snapshot of market data for an asset at a point in time."""

    model_config = {"frozen": True}

    asset: Asset
    timestamp: datetime
    last_tick: Optional[Tick] = None
    best_quote: Optional[Quote] = None
    last_bar: Optional[OHLCVBar] = None


# ══════════════════════════════════════════════════════════════════════════════
# TRADING MODELS
# ══════════════════════════════════════════════════════════════════════════════

class Order(BaseModel):
    """
    Represents a single order throughout its full lifecycle.

    Mutable — status and fill information update as exchange confirms.
    """

    order_id: str = Field(default_factory=_new_uuid)
    strategy_id: Optional[str] = Field(default=None, description="Source strategy identifier")
    asset: Asset
    side: Side
    order_type: OrderType
    quantity: Decimal = Field(..., gt=Decimal("0"))
    limit_price: Optional[Decimal] = Field(
        default=None, description="Limit price; required for LIMIT and STOP_LIMIT orders"
    )
    stop_price: Optional[Decimal] = Field(
        default=None, description="Stop trigger price; required for STOP and STOP_LIMIT orders"
    )
    time_in_force: TimeInForce = Field(default=TimeInForce.DAY)
    product_type: Optional[ProductType] = Field(
        default=None, description="Margin product classification (relevant for Indian markets)"
    )
    status: OrderStatus = Field(default=OrderStatus.PENDING)
    filled_quantity: Decimal = Field(default=Decimal("0"))
    average_fill_price: Optional[Decimal] = Field(default=None)
    broker_order_id: Optional[str] = Field(
        default=None, description="Exchange/broker assigned order ID (populated after submission)"
    )
    created_at: datetime = Field(default_factory=_utc_now)
    updated_at: datetime = Field(default_factory=_utc_now)
    rejected_reason: Optional[str] = Field(default=None)
    tags: dict[str, str] = Field(default_factory=dict, description="Arbitrary key-value metadata")

    @model_validator(mode="after")
    def validate_price_requirements(self) -> "Order":
        if self.order_type in (OrderType.LIMIT, OrderType.STOP_LIMIT) and self.limit_price is None:
            raise ValueError(f"limit_price is required for order_type={self.order_type}")
        if self.order_type in (OrderType.STOP, OrderType.STOP_LIMIT) and self.stop_price is None:
            raise ValueError(f"stop_price is required for order_type={self.order_type}")
        return self

    @property
    def remaining_quantity(self) -> Decimal:
        return self.quantity - self.filled_quantity

    @property
    def is_active(self) -> bool:
        return self.status in (
            OrderStatus.SUBMITTED,
            OrderStatus.OPEN,
            OrderStatus.PARTIALLY_FILLED,
            OrderStatus.PENDING_CANCEL,
            OrderStatus.PENDING_MODIFY,
        )

    @property
    def is_terminal(self) -> bool:
        return self.status in (
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        )


class Fill(BaseModel):
    """Represents a single execution (partial or complete fill) of an order."""

    model_config = {"frozen": True}

    fill_id: str = Field(default_factory=_new_uuid)
    order_id: str
    asset: Asset
    side: Side
    quantity: Decimal = Field(..., gt=Decimal("0"))
    price: Decimal = Field(..., gt=Decimal("0"))
    commission: Decimal = Field(default=Decimal("0"))
    commission_currency: str = Field(default="INR")
    timestamp: datetime

    @field_validator("timestamp")
    @classmethod
    def must_be_tz_aware(cls, v: datetime) -> datetime:
        if v.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return v

    @property
    def gross_value(self) -> Decimal:
        return self.quantity * self.price

    @property
    def net_value(self) -> Decimal:
        return self.gross_value - self.commission


class Position(BaseModel):
    """
    Represents a currently open position in an instrument.

    Updated in real-time as fills arrive.
    """

    asset: Asset
    side: PositionSide = Field(default=PositionSide.FLAT)
    quantity: Decimal = Field(default=Decimal("0"))
    average_entry_price: Decimal = Field(default=Decimal("0"))
    realized_pnl: Decimal = Field(default=Decimal("0"))
    unrealized_pnl: Decimal = Field(default=Decimal("0"))
    last_updated: datetime = Field(default_factory=_utc_now)

    def mark_to_market(self, current_price: Decimal) -> None:
        """Recalculate unrealized P&L given a new market price."""
        if self.side == PositionSide.LONG:
            self.unrealized_pnl = (current_price - self.average_entry_price) * self.quantity
        elif self.side == PositionSide.SHORT:
            self.unrealized_pnl = (self.average_entry_price - current_price) * self.quantity
        else:
            self.unrealized_pnl = Decimal("0")
        self.last_updated = _utc_now()

    @property
    def total_pnl(self) -> Decimal:
        return self.realized_pnl + self.unrealized_pnl


class Trade(BaseModel):
    """
    A completed round-trip trade (entry + exit) for analytics purposes.

    Populated by the analytics module after a position is closed.
    """

    model_config = {"frozen": True}

    trade_id: str = Field(default_factory=_new_uuid)
    strategy_id: Optional[str] = None
    asset: Asset
    side: Side  # Direction of the entry
    entry_time: datetime
    exit_time: datetime
    entry_price: Decimal
    exit_price: Decimal
    quantity: Decimal
    gross_pnl: Decimal
    commission: Decimal
    net_pnl: Decimal

    @property
    def return_pct(self) -> Decimal:
        cost_basis = self.entry_price * self.quantity
        if cost_basis == Decimal("0"):
            return Decimal("0")
        return (self.net_pnl / cost_basis) * Decimal("100")


# ══════════════════════════════════════════════════════════════════════════════
# STRATEGY MODELS
# ══════════════════════════════════════════════════════════════════════════════

class Signal(BaseModel):
    """A trading signal emitted by a strategy."""

    model_config = {"frozen": True}

    signal_id: str = Field(default_factory=_new_uuid)
    strategy_id: str
    asset: Asset
    signal_type: SignalType
    strength: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Signal confidence [0, 1]; None if not applicable",
    )
    suggested_quantity: Optional[Decimal] = Field(default=None)
    suggested_price: Optional[Decimal] = Field(default=None)
    timestamp: datetime = Field(default_factory=_utc_now)
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary indicator values / debug info"
    )


class StrategyMetadata(BaseModel):
    """Static metadata describing a strategy."""

    model_config = {"frozen": True}

    strategy_id: str
    name: str
    version: str = Field(default="0.1.0")
    description: str = Field(default="")
    author: str = Field(default="")
    supported_asset_classes: list[AssetClass] = Field(default_factory=list)
    supported_timeframes: list[Timeframe] = Field(default_factory=list)


class StrategyConfig(BaseModel):
    """
    Runtime configuration for a strategy instance.

    Parameters are stored as a flexible dict to accommodate
    varying strategy logic without a fixed schema per strategy.
    """

    strategy_id: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    risk_per_trade_pct: float = Field(
        default=1.0,
        gt=0.0,
        le=100.0,
        description="Max % of account equity to risk per trade",
    )
    max_open_positions: int = Field(default=1, ge=1)
    state: StrategyState = Field(default=StrategyState.INITIALIZED)


# ══════════════════════════════════════════════════════════════════════════════
# PORTFOLIO MODELS
# ══════════════════════════════════════════════════════════════════════════════

class Balance(BaseModel):
    """Cash / margin balance in a single currency."""

    currency: str = Field(default="INR")
    available: Decimal = Field(default=Decimal("0"))
    used_margin: Decimal = Field(default=Decimal("0"))
    total_equity: Decimal = Field(default=Decimal("0"))

    @property
    def free_margin(self) -> Decimal:
        return self.total_equity - self.used_margin


class Account(BaseModel):
    """Represents a brokerage account."""

    account_id: str
    broker_name: str
    balances: dict[str, Balance] = Field(
        default_factory=dict, description="Keyed by ISO-4217 currency code"
    )
    is_live: bool = Field(
        default=False, description="True = live trading; False = paper/simulation"
    )
    created_at: datetime = Field(default_factory=_utc_now)

    def get_balance(self, currency: str = "INR") -> Optional[Balance]:
        return self.balances.get(currency.upper())


class PortfolioSnapshot(BaseModel):
    """Point-in-time snapshot of the entire portfolio state."""

    model_config = {"frozen": True}

    snapshot_id: str = Field(default_factory=_new_uuid)
    timestamp: datetime
    account_id: str
    positions: list[Position] = Field(default_factory=list)
    total_equity: Decimal = Field(default=Decimal("0"))
    total_unrealized_pnl: Decimal = Field(default=Decimal("0"))
    total_realized_pnl: Decimal = Field(default=Decimal("0"))
    cash_balance: Decimal = Field(default=Decimal("0"))


# ══════════════════════════════════════════════════════════════════════════════
# RISK MODELS
# ══════════════════════════════════════════════════════════════════════════════

class RiskLimits(BaseModel):
    """
    Risk configuration limits for an account or strategy.

    All percentage values are in absolute terms (e.g. 2.0 = 2%).
    """

    max_position_size_pct: float = Field(
        default=10.0,
        gt=0,
        le=100,
        description="Max single position as % of total equity",
    )
    max_daily_loss_pct: float = Field(
        default=3.0,
        gt=0,
        le=100,
        description="Max daily drawdown as % of total equity before halt",
    )
    max_drawdown_pct: float = Field(
        default=15.0,
        gt=0,
        le=100,
        description="Max cumulative drawdown as % of peak equity",
    )
    max_open_positions: int = Field(default=5, ge=1)
    max_order_value: Optional[Decimal] = Field(
        default=None, description="Hard cap on a single order notional value"
    )
    allowed_asset_classes: list[AssetClass] = Field(
        default_factory=lambda: list(AssetClass),
        description="Restrict trading to specified asset classes",
    )


class RiskDecision(BaseModel):
    """The risk engine's verdict on an order request."""

    model_config = {"frozen": True}

    decision: RiskDecisionType
    order_id: str
    reason: Optional[str] = Field(default=None)
    adjusted_quantity: Optional[Decimal] = Field(
        default=None, description="Revised quantity if MODIFIED"
    )
    adjusted_price: Optional[Decimal] = Field(
        default=None, description="Revised price if MODIFIED"
    )
    checked_at: datetime = Field(default_factory=_utc_now)
