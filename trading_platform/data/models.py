"""
Data-layer specific models.

These extend the core domain models with data-pipeline concerns
such as data quality metadata and feed subscription configuration.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from core.enums import Exchange, Timeframe
from core.models import Asset


class DataQualityReport(BaseModel):
    """Tracks data quality metrics for a historical dataset."""

    model_config = {"frozen": True}

    asset: Asset
    timeframe: Timeframe
    start_date: datetime
    end_date: datetime
    total_bars: int
    missing_bars: int
    duplicate_bars: int
    bad_bars: int  # Bars with invalid OHLCV relationships

    @property
    def completeness_pct(self) -> float:
        if self.total_bars == 0:
            return 0.0
        return (1.0 - self.missing_bars / self.total_bars) * 100.0

    @property
    def is_clean(self) -> bool:
        return self.missing_bars == 0 and self.duplicate_bars == 0 and self.bad_bars == 0


class SubscriptionConfig(BaseModel):
    """Configuration for a live market data subscription."""

    asset: Asset
    subscribe_ticks: bool = Field(default=True)
    subscribe_quotes: bool = Field(default=True)
    subscribe_bars: bool = Field(default=False)
    bar_timeframe: Optional[Timeframe] = Field(
        default=None,
        description="If subscribe_bars is True, the timeframe for live bar aggregation",
    )


class DataFeedStatus(BaseModel):
    """Runtime status of a live data feed connection."""

    provider_name: str
    is_connected: bool
    subscribed_symbols: list[str] = Field(default_factory=list)
    last_message_at: Optional[datetime] = None
    error_count: int = Field(default=0)
    reconnect_count: int = Field(default=0)
