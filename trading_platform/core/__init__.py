"""core package — re-exports the primary domain primitives."""

from core.clock import Clock, LiveClock, SimulatedClock
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
from core.events import Event, EventBus
from core.exceptions import TradingPlatformError
from core.models import (
    Account,
    Asset,
    Balance,
    Fill,
    MarketDataSnapshot,
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

__all__ = [
    # Clock
    "Clock", "LiveClock", "SimulatedClock",
    # Enums
    "AssetClass", "EventType", "Exchange", "InstrumentType", "MarketState",
    "OptionStyle", "OptionType", "OrderStatus", "OrderType", "PositionSide",
    "ProductType", "RiskDecisionType", "Side", "SignalType", "StrategyState",
    "Timeframe", "TimeInForce",
    # Events
    "Event", "EventBus",
    # Exceptions
    "TradingPlatformError",
    # Models
    "Account", "Asset", "Balance", "Fill", "MarketDataSnapshot", "OHLCVBar",
    "Order", "PortfolioSnapshot", "Position", "Quote", "RiskDecision",
    "RiskLimits", "Signal", "StrategyConfig", "StrategyMetadata", "Tick",
    "Trade", "TradingSession",
]
