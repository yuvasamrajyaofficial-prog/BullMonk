"""
Market data subsystem for the BullMonk Trading Platform.

Exports:
- Data Providers & Adapters (HistoricalDataProvider, LiveMarketDataProvider, DataProviderRegistry)
- Validation & Normalization (DataValidator, ValidationReport, DataNormalizer)
- Local Cache (DataCache, CacheMetadata)
- Synthetic Market Data Generator (SyntheticOHLCVGenerator, SyntheticDataConfig)
- Session Calendars (NSESessionCalendar, Crypto247SessionCalendar, ForexSessionCalendar, get_session_calendar)
- NIFTY Specifications (create_nifty_index, create_nifty_future, create_nifty_option, generate_nifty_option_chain_metadata)
"""

from data.cache import CacheMetadata, DataCache
from data.interfaces import HistoricalDataProvider, LiveMarketDataProvider, MarketDataProvider
from data.models import DataFeedStatus, DataQualityReport, SubscriptionConfig
from data.nifty import (
    NIFTY_LOT_SIZE,
    NIFTY_STRIKE_INTERVAL,
    NIFTY_SUPPORTED_TIMEFRAMES,
    NIFTY_SYMBOL,
    NiftyOptionChainMetadata,
    NiftyOptionContractMetadata,
    create_nifty_future,
    create_nifty_index,
    create_nifty_option,
    generate_nifty_option_chain_metadata,
    get_nifty_atm_strike,
)
from data.normalization import DataNormalizer
from data.providers import (
    CachedHistoricalDataProvider,
    DataProviderRegistry,
    SimulatedLiveMarketDataProvider,
    SyntheticHistoricalProvider,
)
from data.sessions import (
    Crypto247SessionCalendar,
    ForexSessionCalendar,
    NSESessionCalendar,
    SessionCalendar,
    SessionWindow,
    USSessionCalendar,
    get_session_calendar,
)
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
from data.validation import (
    DataValidator,
    ValidationErrorType,
    ValidationIssue,
    ValidationReport,
    ValidationSeverity,
)

__all__ = [
    # Interfaces
    "MarketDataProvider",
    "HistoricalDataProvider",
    "LiveMarketDataProvider",
    # Models & Reports
    "DataQualityReport",
    "SubscriptionConfig",
    "DataFeedStatus",
    "ValidationReport",
    "ValidationIssue",
    "ValidationErrorType",
    "ValidationSeverity",
    # Validation & Normalization
    "DataValidator",
    "DataNormalizer",
    # Cache
    "DataCache",
    "CacheMetadata",
    # Synthetic Generator
    "SyntheticOHLCVGenerator",
    "SyntheticDataConfig",
    # Sessions
    "SessionCalendar",
    "SessionWindow",
    "NSESessionCalendar",
    "Crypto247SessionCalendar",
    "ForexSessionCalendar",
    "USSessionCalendar",
    "get_session_calendar",
    # NIFTY
    "NIFTY_SYMBOL",
    "NIFTY_LOT_SIZE",
    "NIFTY_STRIKE_INTERVAL",
    "NIFTY_SUPPORTED_TIMEFRAMES",
    "create_nifty_index",
    "create_nifty_future",
    "create_nifty_option",
    "get_nifty_atm_strike",
    "generate_nifty_option_chain_metadata",
    "NiftyOptionChainMetadata",
    "NiftyOptionContractMetadata",
    # Providers
    "SyntheticHistoricalProvider",
    "CachedHistoricalDataProvider",
    "SimulatedLiveMarketDataProvider",
    "DataProviderRegistry",
]
