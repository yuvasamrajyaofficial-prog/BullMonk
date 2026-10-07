"""
Unit tests for the configuration system.

Tests that:
1. Settings can be instantiated with defaults.
2. Environment variable overrides work.
3. Invalid values raise ValidationError.
4. No secrets are hard-coded.
5. Production validation helper works.
"""

from __future__ import annotations

import os
import pytest
from unittest.mock import patch

from config.settings import Settings, get_settings


class TestSettingsDefaults:
    def test_default_environment(self):
        s = Settings()
        assert s.environment == "development"

    def test_default_log_level(self):
        s = Settings()
        assert s.log_level == "INFO"

    def test_default_debug_false(self):
        s = Settings()
        assert s.debug is False

    def test_app_name_present(self):
        s = Settings()
        assert s.app_name  # non-empty

    def test_default_credentials_are_none(self):
        """Secrets must not be hard-coded — all None by default."""
        s = Settings()
        assert s.dhan_client_id is None
        assert s.dhan_access_token is None
        assert s.zerodha_api_key is None
        assert s.zerodha_access_token is None
        assert s.binance_api_key is None
        assert s.binance_secret is None
        assert s.jwt_secret is None
        assert s.database_url is None
        assert s.redis_url is None

    def test_default_risk_limits(self):
        s = Settings()
        assert s.default_max_daily_loss_pct == 3.0
        assert s.default_max_drawdown_pct == 15.0
        assert s.default_max_open_positions == 5


class TestSettingsValidation:
    def test_invalid_environment_raises(self):
        with pytest.raises(Exception):
            Settings(environment="invalid_env")

    def test_invalid_log_level_raises(self):
        with pytest.raises(Exception):
            Settings(log_level="VERBOSE")

    def test_valid_environments(self):
        for env in ["development", "staging", "production"]:
            s = Settings(environment=env)
            assert s.environment == env

    def test_valid_log_levels(self):
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            s = Settings(log_level=level)
            assert s.log_level == level


class TestSettingsEnvOverride:
    def test_env_var_sets_debug(self):
        with patch.dict(os.environ, {"DEBUG": "true"}):
            s = Settings()
            assert s.debug is True

    def test_env_var_sets_log_level(self):
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}):
            s = Settings()
            assert s.log_level == "DEBUG"

    def test_env_var_sets_dhan_client_id(self):
        with patch.dict(os.environ, {"DHAN_CLIENT_ID": "test_client_123"}):
            s = Settings()
            assert s.dhan_client_id == "test_client_123"


class TestProductionValidation:
    def test_missing_production_requirements(self):
        s = Settings(environment="production")
        missing = s.validate_production_requirements()
        # All three are missing by default
        assert "DATABASE_URL" in missing
        assert "REDIS_URL" in missing
        assert "JWT_SECRET" in missing

    def test_is_production(self):
        s = Settings(environment="production")
        assert s.is_production
        assert not s.is_development

    def test_is_development(self):
        s = Settings(environment="development")
        assert s.is_development
        assert not s.is_production
