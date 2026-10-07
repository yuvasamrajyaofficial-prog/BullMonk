"""
Synthetic historical data provider adapter.

Provides deterministic, offline OHLCV bars using the SyntheticOHLCVGenerator.
Ideal for development, integration tests, and reproducible quantitative research.
Explicitly flags all generated bars with DataSource.SYNTHETIC.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from core.enums import DataSource, Timeframe
from core.models import Asset, OHLCVBar
from data.interfaces import HistoricalDataProvider
from data.nifty import create_nifty_index
from data.sessions import get_session_calendar
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator


class SyntheticHistoricalProvider(HistoricalDataProvider):
    """
    HistoricalDataProvider adapter generating synthetic bars on-demand.
    Never connects to external networks; completely offline and deterministic.
    """

    def __init__(
        self,
        seed: int = 42,
        volatility: float = 0.16,
        drift: float = 0.05,
    ) -> None:
        self._seed = seed
        self._volatility = volatility
        self._drift = drift
        self._generator = SyntheticOHLCVGenerator(seed=seed)
        self._supported_assets: list[Asset] = [create_nifty_index()]

    def get_name(self) -> str:
        return "SyntheticHistoricalProvider"

    def register_asset(self, asset: Asset) -> None:
        """Register an asset as available in this provider."""
        if not any(a.symbol == asset.symbol and a.exchange == asset.exchange for a in self._supported_assets):
            self._supported_assets.append(asset)

    def get_assets(self) -> list[Asset]:
        return list(self._supported_assets)

    def get_bars(
        self,
        asset: Asset,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
        *,
        limit: Optional[int] = None,
    ) -> list[OHLCVBar]:
        """
        Fetch synthetic historical bars within [start, end].
        """
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("start and end datetimes must be timezone-aware (UTC)")

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        if start_utc > end_utc:
            raise ValueError(f"start ({start_utc}) cannot be after end ({end_utc})")

        calendar = get_session_calendar(asset.exchange)
        start_date = start_utc.date()
        end_date = end_utc.date()

        days_count = (end_date - start_date).days + 1
        num_sessions = max(days_count, 1)

        # Baseline starting price
        base_price = Decimal("24000.00") if asset.symbol == "NIFTY" else Decimal("1000.00")

        cfg = SyntheticDataConfig(
            asset=asset,
            start_price=base_price,
            volatility=self._volatility,
            drift=self._drift,
            session_calendar=calendar,
            number_of_sessions=num_sessions,
            timeframe=timeframe,
            seed=self._seed,
            start_date=start_date,
        )

        all_bars = self._generator.generate(cfg)

        # Filter strictly within [start_utc, end_utc]
        filtered_bars = [
            b for b in all_bars
            if start_utc <= b.timestamp <= end_utc
        ]

        if limit is not None and limit > 0:
            filtered_bars = filtered_bars[-limit:]

        return filtered_bars

    def get_latest_bar(
        self,
        asset: Asset,
        timeframe: Timeframe,
    ) -> Optional[OHLCVBar]:
        """Return the most recently generated bar for the asset."""
        now = datetime.now(tz=timezone.utc)
        # Generate 1 session worth of recent bars
        bars = self.get_bars(asset, timeframe, now.replace(hour=0, minute=0, second=0), now)
        return bars[-1] if bars else None
