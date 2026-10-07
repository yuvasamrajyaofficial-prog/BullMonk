"""
Domain-level exceptions for the trading platform.

All platform-specific exceptions inherit from TradingPlatformError,
allowing callers to catch the full family with a single clause.

Design principles:
- Never silently swallow exceptions.
- Exceptions carry context (instrument, order ID, broker name, etc.)
  so that logs are actionable without additional lookups.
- No broker-specific language in base exceptions.
"""

from __future__ import annotations


# ──────────────────────────────────────────────
# Root
# ──────────────────────────────────────────────

class TradingPlatformError(Exception):
    """Base exception for the entire trading platform."""


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

class ConfigurationError(TradingPlatformError):
    """Raised when a required configuration value is missing or invalid."""


class MissingEnvironmentVariable(ConfigurationError):
    """Raised when a required environment variable is not set."""

    def __init__(self, variable_name: str) -> None:
        self.variable_name = variable_name
        super().__init__(
            f"Required environment variable '{variable_name}' is not set. "
            "Check your .env file and the .env.example template."
        )


# ──────────────────────────────────────────────
# Market Data
# ──────────────────────────────────────────────

class MarketDataError(TradingPlatformError):
    """Base class for market data related errors."""


class DataProviderError(MarketDataError):
    """Raised when a data provider fails to return data."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        super().__init__(f"[DataProvider={provider}] {message}")


class DataNotFoundError(MarketDataError):
    """Raised when requested data does not exist."""

    def __init__(self, symbol: str, detail: str = "") -> None:
        self.symbol = symbol
        msg = f"No data found for symbol '{symbol}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class InvalidBarError(MarketDataError):
    """Raised when a bar's OHLCV values are logically inconsistent."""

    def __init__(self, symbol: str, detail: str) -> None:
        self.symbol = symbol
        super().__init__(f"Invalid bar for '{symbol}': {detail}")


# ──────────────────────────────────────────────
# Order / Execution
# ──────────────────────────────────────────────

class OrderError(TradingPlatformError):
    """Base class for order related errors."""


class OrderValidationError(OrderError):
    """Raised when an order fails pre-submission validation."""

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        super().__init__(f"Order validation failed on field '{field}': {reason}")


class OrderRejectedError(OrderError):
    """Raised when a broker/exchange rejects an order."""

    def __init__(self, order_id: str, reason: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' rejected: {reason}")


class OrderNotFoundError(OrderError):
    """Raised when an order ID cannot be located."""

    def __init__(self, order_id: str) -> None:
        self.order_id = order_id
        super().__init__(f"Order '{order_id}' not found.")


class OrderModificationError(OrderError):
    """Raised when an order modification request fails."""

    def __init__(self, order_id: str, reason: str) -> None:
        self.order_id = order_id
        super().__init__(f"Failed to modify order '{order_id}': {reason}")


class OrderCancellationError(OrderError):
    """Raised when an order cancellation request fails."""

    def __init__(self, order_id: str, reason: str) -> None:
        self.order_id = order_id
        super().__init__(f"Failed to cancel order '{order_id}': {reason}")


class InsufficientFundsError(OrderError):
    """Raised when an account has insufficient margin or cash."""

    def __init__(self, required: float, available: float, currency: str = "INR") -> None:
        self.required = required
        self.available = available
        self.currency = currency
        super().__init__(
            f"Insufficient funds: required {required:.2f} {currency}, "
            f"available {available:.2f} {currency}."
        )


# ──────────────────────────────────────────────
# Broker / Connectivity
# ──────────────────────────────────────────────

class BrokerError(TradingPlatformError):
    """Base class for broker adapter errors."""


class BrokerConnectionError(BrokerError):
    """Raised when a connection to a broker API cannot be established."""

    def __init__(self, broker_name: str, detail: str = "") -> None:
        self.broker_name = broker_name
        msg = f"Cannot connect to broker '{broker_name}'"
        if detail:
            msg += f": {detail}"
        super().__init__(msg)


class BrokerAuthenticationError(BrokerError):
    """Raised when broker credentials are invalid or expired."""

    def __init__(self, broker_name: str) -> None:
        self.broker_name = broker_name
        super().__init__(
            f"Authentication failed for broker '{broker_name}'. "
            "Check your credentials and token expiry."
        )


class BrokerRateLimitError(BrokerError):
    """Raised when the broker API rate limit is exceeded."""

    def __init__(self, broker_name: str, retry_after_seconds: float | None = None) -> None:
        self.broker_name = broker_name
        self.retry_after_seconds = retry_after_seconds
        msg = f"Rate limit exceeded for broker '{broker_name}'"
        if retry_after_seconds is not None:
            msg += f". Retry after {retry_after_seconds:.0f}s."
        super().__init__(msg)


# ──────────────────────────────────────────────
# Strategy
# ──────────────────────────────────────────────

class StrategyError(TradingPlatformError):
    """Base class for strategy-related errors."""


class StrategyInitializationError(StrategyError):
    """Raised when a strategy fails to initialize."""

    def __init__(self, strategy_id: str, reason: str) -> None:
        self.strategy_id = strategy_id
        super().__init__(f"Strategy '{strategy_id}' failed to initialize: {reason}")


class StrategyRuntimeError(StrategyError):
    """Raised when a strategy encounters an error during execution."""

    def __init__(self, strategy_id: str, reason: str) -> None:
        self.strategy_id = strategy_id
        super().__init__(f"Strategy '{strategy_id}' runtime error: {reason}")


# ──────────────────────────────────────────────
# Risk
# ──────────────────────────────────────────────

class RiskError(TradingPlatformError):
    """Base class for risk management errors."""


class RiskLimitBreachError(RiskError):
    """Raised when a risk limit is breached."""

    def __init__(self, limit_name: str, current: float, limit: float) -> None:
        self.limit_name = limit_name
        self.current = current
        self.limit = limit
        super().__init__(
            f"Risk limit breached: '{limit_name}' = {current:.4f} exceeds limit {limit:.4f}."
        )


# ──────────────────────────────────────────────
# Portfolio
# ──────────────────────────────────────────────

class PortfolioError(TradingPlatformError):
    """Base class for portfolio management errors."""


class PositionNotFoundError(PortfolioError):
    """Raised when a position for a given instrument is not found."""

    def __init__(self, symbol: str) -> None:
        self.symbol = symbol
        super().__init__(f"No open position found for symbol '{symbol}'.")


# ──────────────────────────────────────────────
# Backtesting
# ──────────────────────────────────────────────

class BacktestError(TradingPlatformError):
    """Base class for backtesting errors."""


class InsufficientDataError(BacktestError):
    """Raised when there is not enough historical data to run a backtest."""

    def __init__(self, symbol: str, required_bars: int, available_bars: int) -> None:
        self.symbol = symbol
        super().__init__(
            f"Insufficient data for '{symbol}': "
            f"required {required_bars} bars, got {available_bars}."
        )


# ──────────────────────────────────────────────
# Clock / Time
# ──────────────────────────────────────────────

class ClockError(TradingPlatformError):
    """Raised when the platform clock encounters an inconsistency."""
