"""
Centralised logging configuration.

Provides structured JSON logging with separate log channels:
- application  : General platform log
- trading      : Order lifecycle and trade events
- risk         : Risk limit breaches and decisions
- errors       : Unhandled exceptions and critical errors

Usage:
    from logging_config import configure_logging, get_logger

    configure_logging()  # Call once at startup
    logger = get_logger("trading")
    logger.info("Order placed", extra={"order_id": "..."})

Security:
    Tokens, secrets, and passwords must NEVER be passed to log calls.
    The SanitizingFilter below redacts common secret patterns as a
    last-resort guard, but the primary responsibility lies with callers.
"""

from __future__ import annotations

import logging
import logging.config
import re
import sys
from typing import Optional

# ──────────────────────────────────────────────
# Logger names (constants for type-safe access)
# ──────────────────────────────────────────────

LOG_APP = "trading_platform.app"
LOG_TRADING = "trading_platform.trading"
LOG_ORDERS = "trading_platform.orders"
LOG_RISK = "trading_platform.risk"
LOG_ERRORS = "trading_platform.errors"

# ──────────────────────────────────────────────
# Secret pattern filter (last-resort redaction)
# ──────────────────────────────────────────────

_SECRET_PATTERNS = re.compile(
    r"(access[_-]?token|api[_-]?key|secret|password|passwd|token|jwt|bearer)\s*[=:]\s*\S+",
    flags=re.IGNORECASE,
)
_REDACTED = r"\1=<REDACTED>"


class SanitizingFilter(logging.Filter):
    """
    Redacts credential-like strings from log records.

    This is a safety net, NOT a primary control. Code must not
    log secrets in the first place.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        if isinstance(record.msg, str):
            record.msg = _SECRET_PATTERNS.sub(_REDACTED, record.msg)
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(
                    _SECRET_PATTERNS.sub(_REDACTED, str(a)) if isinstance(a, str) else a
                    for a in record.args
                )
        return True


# ──────────────────────────────────────────────
# Formatter
# ──────────────────────────────────────────────

CONSOLE_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)

DETAILED_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | "
    "%(filename)s:%(lineno)d | %(funcName)s | %(message)s"
)


# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

def configure_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    json_output: bool = False,
) -> None:
    """
    Configure the platform logging system.

    Call this ONCE at application startup, before any other imports
    that use the logging system.

    Args:
        level:       Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        log_file:    Optional path to a file sink. If None, logs go to stdout only.
        json_output: If True, emit JSON-formatted log lines (for log aggregators).
                     Phase 1 uses plain text; JSON available as future upgrade.
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    handlers: dict = {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "detailed",
            "filters": ["sanitize"],
        }
    }

    if log_file:
        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": log_file,
            "maxBytes": 10 * 1024 * 1024,  # 10 MB
            "backupCount": 5,
            "formatter": "detailed",
            "filters": ["sanitize"],
            "encoding": "utf-8",
        }

    active_handlers = list(handlers.keys())

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {
            "sanitize": {
                "()": SanitizingFilter,
            }
        },
        "formatters": {
            "console": {"format": CONSOLE_FORMAT},
            "detailed": {"format": DETAILED_FORMAT},
        },
        "handlers": handlers,
        "loggers": {
            # Platform namespaces — each can be given its own handler later
            LOG_APP: {"level": level.upper(), "handlers": active_handlers, "propagate": False},
            LOG_TRADING: {"level": level.upper(), "handlers": active_handlers, "propagate": False},
            LOG_ORDERS: {"level": level.upper(), "handlers": active_handlers, "propagate": False},
            LOG_RISK: {"level": level.upper(), "handlers": active_handlers, "propagate": False},
            LOG_ERRORS: {"level": "WARNING", "handlers": active_handlers, "propagate": False},
            # Root logger (catch-all)
            "root": {"level": level.upper(), "handlers": active_handlers},
        },
    }

    logging.config.dictConfig(logging_config)
    logging.getLogger(LOG_APP).info(
        "Logging configured: level=%s file=%s", level.upper(), log_file or "stdout"
    )


def get_logger(channel: str = "app") -> logging.Logger:
    """
    Return a named logger for a specific platform channel.

    Args:
        channel: One of 'app', 'trading', 'orders', 'risk', 'errors'.
                 Defaults to 'app'.

    Returns:
        Configured Logger instance.
    """
    mapping = {
        "app": LOG_APP,
        "trading": LOG_TRADING,
        "orders": LOG_ORDERS,
        "risk": LOG_RISK,
        "errors": LOG_ERRORS,
    }
    logger_name = mapping.get(channel.lower(), LOG_APP)
    return logging.getLogger(logger_name)
