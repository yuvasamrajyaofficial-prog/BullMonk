"""
Core enumerations for the trading platform.

These enums are domain-level constructs that remain broker-agnostic.
They represent the fundamental vocabulary of the trading system.
"""

from enum import Enum, auto


# ──────────────────────────────────────────────
# Market / Instrument classification
# ──────────────────────────────────────────────

class AssetClass(str, Enum):
    """Broad classification of the tradable asset."""
    EQUITY = "EQUITY"
    FUTURES = "FUTURES"
    OPTIONS = "OPTIONS"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    BOND = "BOND"
    ETF = "ETF"


class InstrumentType(str, Enum):
    """Fine-grained instrument type within an asset class."""
    STOCK = "STOCK"                   # e.g. RELIANCE, TCS
    INDEX = "INDEX"                   # e.g. NIFTY50 (non-tradable index)
    INDEX_FUTURES = "INDEX_FUTURES"   # e.g. NIFTY FUT
    INDEX_OPTIONS = "INDEX_OPTIONS"   # e.g. NIFTY CE / PE
    STOCK_FUTURES = "STOCK_FUTURES"
    STOCK_OPTIONS = "STOCK_OPTIONS"
    CURRENCY_PAIR = "CURRENCY_PAIR"   # e.g. EURUSD
    CRYPTO_SPOT = "CRYPTO_SPOT"       # e.g. BTC/USDT spot
    CRYPTO_FUTURES = "CRYPTO_FUTURES"
    CRYPTO_OPTIONS = "CRYPTO_OPTIONS"
    COMMODITY_FUTURES = "COMMODITY_FUTURES"
    GOVERNMENT_BOND = "GOVERNMENT_BOND"
    CORPORATE_BOND = "CORPORATE_BOND"
    ETF = "ETF"


class Exchange(str, Enum):
    """Supported exchanges and venues."""
    # Indian
    NSE = "NSE"          # National Stock Exchange of India
    BSE = "BSE"          # Bombay Stock Exchange
    NFO = "NFO"          # NSE Futures & Options
    BFO = "BFO"          # BSE Futures & Options
    CDS = "CDS"          # Currency Derivatives Segment
    MCX = "MCX"          # Multi Commodity Exchange
    # Global equity
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    # Forex
    FOREX_OTC = "FOREX_OTC"
    # Crypto
    BINANCE = "BINANCE"
    COINBASE = "COINBASE"
    BYBIT = "BYBIT"
    # Generic / unknown
    UNKNOWN = "UNKNOWN"


class OptionType(str, Enum):
    """Option contract type."""
    CALL = "CE"
    PUT = "PE"


class OptionStyle(str, Enum):
    """Option exercise style."""
    EUROPEAN = "EUROPEAN"
    AMERICAN = "AMERICAN"


# ──────────────────────────────────────────────
# Trading
# ──────────────────────────────────────────────

class Side(str, Enum):
    """Order / position side."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order execution type."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"              # Stop market order
    STOP_LIMIT = "STOP_LIMIT"  # Stop limit order
    TRAILING_STOP = "TRAILING_STOP"


class TimeInForce(str, Enum):
    """Order validity / time-in-force."""
    DAY = "DAY"        # Valid for the trading day
    GTC = "GTC"        # Good-till-cancelled
    IOC = "IOC"        # Immediate-or-cancel
    FOK = "FOK"        # Fill-or-kill
    GTD = "GTD"        # Good-till-date
    ATO = "ATO"        # At the opening
    ATC = "ATC"        # At the closing


class OrderStatus(str, Enum):
    """Lifecycle status of an order."""
    PENDING = "PENDING"           # Created locally, not yet submitted
    SUBMITTED = "SUBMITTED"       # Sent to broker
    OPEN = "OPEN"                 # Acknowledged and resting on exchange
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    PENDING_CANCEL = "PENDING_CANCEL"
    PENDING_MODIFY = "PENDING_MODIFY"


class ProductType(str, Enum):
    """Margin / delivery product classification (Indian markets)."""
    CNC = "CNC"        # Cash-and-carry (equity delivery)
    MIS = "MIS"        # Margin intra-day settlement
    NRML = "NRML"      # Normal carry-forward F&O


class PositionSide(str, Enum):
    """Net direction of a position."""
    LONG = "LONG"
    SHORT = "SHORT"
    FLAT = "FLAT"


# ──────────────────────────────────────────────
# Strategy
# ──────────────────────────────────────────────

class SignalType(str, Enum):
    """Trading signal classification."""
    ENTER_LONG = "ENTER_LONG"
    ENTER_SHORT = "ENTER_SHORT"
    EXIT_LONG = "EXIT_LONG"
    EXIT_SHORT = "EXIT_SHORT"
    SCALE_IN = "SCALE_IN"
    SCALE_OUT = "SCALE_OUT"
    NO_SIGNAL = "NO_SIGNAL"
    CLOSE_ALL = "CLOSE_ALL"


class StrategyState(str, Enum):
    """Lifecycle state of a strategy instance."""
    INITIALIZED = "INITIALIZED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPED = "STOPPED"
    ERROR = "ERROR"


# ──────────────────────────────────────────────
# Timeframes
# ──────────────────────────────────────────────

class Timeframe(str, Enum):
    """OHLCV bar timeframe."""
    S1 = "1s"
    M1 = "1m"
    M2 = "2m"
    M3 = "3m"
    M5 = "5m"
    M10 = "10m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H2 = "2h"
    H4 = "4h"
    D1 = "1d"
    W1 = "1w"
    MN1 = "1M"


# ──────────────────────────────────────────────
# Data provenance
# ──────────────────────────────────────────────

class DataSource(str, Enum):
    """Origin and provenance of market data."""
    REAL = "REAL"
    SYNTHETIC = "SYNTHETIC"
    BACKTEST_SIMULATED = "BACKTEST_SIMULATED"


# ──────────────────────────────────────────────
# Risk
# ──────────────────────────────────────────────

class RiskDecisionType(str, Enum):
    """Risk engine verdict for an order request."""
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MODIFIED = "MODIFIED"  # Approved with qty/price adjustment


# ──────────────────────────────────────────────
# Events
# ──────────────────────────────────────────────

class EventType(str, Enum):
    """Domain event types flowing through the event bus."""
    MARKET_DATA = "MARKET_DATA"
    BAR = "BAR"
    TICK = "TICK"
    QUOTE = "QUOTE"
    SIGNAL = "SIGNAL"
    ORDER_REQUEST = "ORDER_REQUEST"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    ORDER_FILLED = "ORDER_FILLED"
    ORDER_CANCELLED = "ORDER_CANCELLED"
    ORDER_REJECTED = "ORDER_REJECTED"
    POSITION_UPDATED = "POSITION_UPDATED"
    RISK_BREACH = "RISK_BREACH"
    STRATEGY_START = "STRATEGY_START"
    STRATEGY_STOP = "STRATEGY_STOP"
    HEARTBEAT = "HEARTBEAT"
    ERROR = "ERROR"


# ──────────────────────────────────────────────
# Session / Market state
# ──────────────────────────────────────────────

class MarketState(str, Enum):
    """Current state of the market / trading session."""
    PRE_OPEN = "PRE_OPEN"
    OPEN = "OPEN"
    POST_CLOSE = "POST_CLOSE"
    CLOSED = "CLOSED"
    HALT = "HALT"
    UNKNOWN = "UNKNOWN"
