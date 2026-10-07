"""Strategy-layer supplementary models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from pydantic import BaseModel, Field

from core.enums import AssetClass, StrategyState, Timeframe


class IndicatorValue(BaseModel):
    """A single computed indicator value at a point in time."""

    model_config = {"frozen": True}

    name: str
    value: Decimal
    timestamp: datetime


class StrategyPerformanceSummary(BaseModel):
    """Lightweight performance summary emitted by a strategy at runtime."""

    model_config = {"frozen": True}

    strategy_id: str
    total_signals: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_trades: int = 0
    gross_pnl: Decimal = Field(default=Decimal("0"))
    net_pnl: Decimal = Field(default=Decimal("0"))
    max_drawdown: Decimal = Field(default=Decimal("0"))
    state: StrategyState = StrategyState.INITIALIZED

    @property
    def win_rate(self) -> float:
        if self.total_trades == 0:
            return 0.0
        return self.winning_trades / self.total_trades
