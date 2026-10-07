"""
Centralised platform configuration.

All settings are loaded exclusively from environment variables.
Secrets are NEVER committed to source control.

Usage:
    from config.settings import settings
    print(settings.database_url)

The Settings object is a singleton — import `settings` not `Settings`.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Platform-wide settings loaded from environment variables.

    Required variables that have no default will raise a ValidationError
    on startup if missing — fail-fast is intentional.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Unknown env vars are silently ignored
    )

    # ──────────────────────────────────────────────
    # Application
    # ──────────────────────────────────────────────

    app_name: str = Field(default="BullMonk Trading Platform")
    app_version: str = Field(default="0.1.0")
    environment: str = Field(
        default="development",
        description="One of: development, staging, production",
    )
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"environment must be one of {allowed}, got '{v}'")
        return v.lower()

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if v.upper() not in allowed:
            raise ValueError(f"log_level must be one of {allowed}, got '{v}'")
        return v.upper()

    # ──────────────────────────────────────────────
    # Infrastructure
    # ──────────────────────────────────────────────

    database_url: Optional[str] = Field(
        default=None,
        description="PostgreSQL connection string. Required in staging/production.",
    )
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection string. Required for live trading cache.",
    )

    # ──────────────────────────────────────────────
    # Security
    # ──────────────────────────────────────────────

    jwt_secret: Optional[str] = Field(
        default=None,
        description="Secret key for JWT token signing. Required for API auth.",
    )

    # ──────────────────────────────────────────────
    # Dhan (Indian broker)
    # ──────────────────────────────────────────────

    dhan_client_id: Optional[str] = Field(
        default=None,
        description="Dhan client/user ID. Required when using Dhan broker adapter.",
    )
    dhan_access_token: Optional[str] = Field(
        default=None,
        description="Dhan API access token. Required when using Dhan broker adapter.",
    )

    # ──────────────────────────────────────────────
    # Zerodha (future)
    # ──────────────────────────────────────────────

    zerodha_api_key: Optional[str] = Field(default=None)
    zerodha_access_token: Optional[str] = Field(default=None)

    # ──────────────────────────────────────────────
    # Binance (future)
    # ──────────────────────────────────────────────

    binance_api_key: Optional[str] = Field(default=None)
    binance_secret: Optional[str] = Field(default=None)

    # ──────────────────────────────────────────────
    # Upstox (future)
    # ──────────────────────────────────────────────

    upstox_api_key: Optional[str] = Field(default=None)
    upstox_access_token: Optional[str] = Field(default=None)

    # ──────────────────────────────────────────────
    # Fyers (future)
    # ──────────────────────────────────────────────

    fyers_app_id: Optional[str] = Field(default=None)
    fyers_access_token: Optional[str] = Field(default=None)

    # ──────────────────────────────────────────────
    # Risk defaults
    # ──────────────────────────────────────────────

    default_max_daily_loss_pct: float = Field(
        default=3.0,
        description="Default daily loss limit as % of equity",
    )
    default_max_drawdown_pct: float = Field(
        default=15.0,
        description="Default maximum drawdown limit as % of peak equity",
    )
    default_max_open_positions: int = Field(default=5)

    # ──────────────────────────────────────────────
    # Helpers
    # ──────────────────────────────────────────────

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    def validate_production_requirements(self) -> list[str]:
        """
        Return a list of missing required fields for production.

        Returns:
            List of missing variable names (empty = all good).
        """
        missing = []
        if not self.database_url:
            missing.append("DATABASE_URL")
        if not self.redis_url:
            missing.append("REDIS_URL")
        if not self.jwt_secret:
            missing.append("JWT_SECRET")
        return missing


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return the singleton Settings instance.

    Cached after first call. Do not call get_settings() inside module-level
    code that runs at import time; always call inside functions.
    """
    s = Settings()
    logger.debug(
        "Settings loaded: app=%s env=%s log_level=%s debug=%s",
        s.app_name,
        s.environment,
        s.log_level,
        s.debug,
    )
    return s


# Convenience singleton for direct import
settings = get_settings()
