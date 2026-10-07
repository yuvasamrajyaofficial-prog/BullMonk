"""
Market data normalization and timeframe resampling engine.

Provides:
- Timezone normalization (UTC conversion)
- Strict chronological sorting
- Deduplication of duplicate timestamps
- Precision and tick size alignment
- Multi-timeframe bar aggregation/resampling (e.g. 1m -> 5m, 15m, 30m, 1h, 1d)
  with exact candlestick aggregation:
  Open = first open, High = max(highs), Low = min(lows), Close = last close, Volume = sum(volumes)
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Callable, Optional

from core.enums import DataSource, Timeframe
from core.models import Asset, OHLCVBar
from data.sessions import _timeframe_to_timedelta


class DataNormalizer:
    """
    Normalizes raw and historical bar sequences to clean platform standards.
    """

    @staticmethod
    def ensure_utc(dt: datetime) -> datetime:
        """Convert datetime to UTC timezone-aware."""
        if dt.tzinfo is None:
            # Assume UTC if naive, or convert
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def normalize_bars(
        self,
        bars: list[OHLCVBar],
        deduplicate_strategy: str = "last",
        enforce_tick_size: bool = True,
    ) -> list[OHLCVBar]:
        """
        Normalize a sequence of OHLCV bars:
        1. Ensures UTC timezone on all timestamps.
        2. Deduplicates timestamps using specified strategy ('last', 'first', 'max_volume').
        3. Sorts chronologically ascending.
        4. Aligns prices to asset tick size if requested.
        5. Preserves data provenance (DataSource.SYNTHETIC).

        Args:
            bars: Input list of bars.
            deduplicate_strategy: 'last', 'first', or 'max_volume'.
            enforce_tick_size: Whether to snap prices to asset.tick_size.

        Returns:
            New list of normalized OHLCVBar objects in ascending order.
        """
        if not bars:
            return []

        # 1. Ensure UTC & group by timestamp
        groups: dict[datetime, list[OHLCVBar]] = defaultdict(list)
        for b in bars:
            utc_ts = self.ensure_utc(b.timestamp)
            groups[utc_ts].append(b)

        # 2. Deduplicate
        deduped: list[OHLCVBar] = []
        for ts, grouped_bars in groups.items():
            if len(grouped_bars) == 1:
                deduped.append(grouped_bars[0])
            else:
                if deduplicate_strategy == "first":
                    deduped.append(grouped_bars[0])
                elif deduplicate_strategy == "max_volume":
                    chosen = max(grouped_bars, key=lambda x: x.volume)
                    deduped.append(chosen)
                else:  # default "last"
                    deduped.append(grouped_bars[-1])

        # 3. Sort chronologically
        deduped.sort(key=lambda b: self.ensure_utc(b.timestamp))

        # 4. Align prices & enforce invariants
        normalized: list[OHLCVBar] = []
        for b in deduped:
            asset = b.asset
            tick = asset.tick_size or Decimal("0.05") if enforce_tick_size else None

            open_p = self._round_tick(b.open, tick) if tick else b.open
            high_p = self._round_tick(b.high, tick) if tick else b.high
            low_p = self._round_tick(b.low, tick) if tick else b.low
            close_p = self._round_tick(b.close, tick) if tick else b.close

            # Ensure invariants hold
            high_p = max(high_p, open_p, close_p)
            low_p = min(low_p, open_p, close_p)
            vol = max(Decimal("0"), b.volume)

            norm_bar = OHLCVBar(
                asset=b.asset,
                timeframe=b.timeframe,
                timestamp=self.ensure_utc(b.timestamp),
                open=open_p,
                high=high_p,
                low=low_p,
                close=close_p,
                volume=vol,
                open_interest=b.open_interest,
                data_source=b.data_source,
            )
            normalized.append(norm_bar)

        return normalized

    def resample_bars(
        self,
        bars: list[OHLCVBar],
        target_timeframe: Timeframe,
    ) -> list[OHLCVBar]:
        """
        Aggregate lower timeframe bars into higher timeframe bars.
        e.g. 1m -> 5m, 15m, 30m, 1h, 1d.

        Aggregation rules:
        - Open = first bar's open
        - High = max(highs)
        - Low = min(lows)
        - Close = last bar's close
        - Volume = sum(volumes)
        - Open Interest = last bar's open_interest
        - DataSource = SYNTHETIC if any source bar is SYNTHETIC, else REAL.

        Args:
            bars: Source bars (must be normalized and sorted).
            target_timeframe: Target aggregation timeframe.

        Returns:
            List of aggregated OHLCVBar objects in target timeframe.
        """
        if not bars:
            return []

        clean_bars = self.normalize_bars(bars)
        target_delta = _timeframe_to_timedelta(target_timeframe)
        target_seconds = int(target_delta.total_seconds())

        # Group bars into target time buckets
        buckets: dict[datetime, list[OHLCVBar]] = defaultdict(list)

        for b in clean_bars:
            ts = b.timestamp
            # For daily bar, bucket by start of day (or session open)
            if target_timeframe == Timeframe.D1:
                bucket_key = datetime(ts.year, ts.month, ts.day, 0, 0, tzinfo=timezone.utc)
            else:
                epoch_sec = int(ts.timestamp())
                bucket_epoch = (epoch_sec // target_seconds) * target_seconds
                bucket_key = datetime.fromtimestamp(bucket_epoch, tz=timezone.utc)
            buckets[bucket_key].append(b)

        aggregated: list[OHLCVBar] = []
        for bucket_ts in sorted(buckets.keys()):
            chunk = buckets[bucket_ts]
            if not chunk:
                continue

            first_bar = chunk[0]
            last_bar = chunk[-1]

            open_p = first_bar.open
            close_p = last_bar.close
            high_p = max(b.high for b in chunk)
            low_p = min(b.low for b in chunk)
            total_vol = sum((b.volume for b in chunk), Decimal("0"))
            last_oi = last_bar.open_interest

            # Retain synthetic provenance if any constituent bar was synthetic
            is_any_synthetic = any(b.data_source == DataSource.SYNTHETIC for b in chunk)
            data_source = DataSource.SYNTHETIC if is_any_synthetic else first_bar.data_source

            agg_bar = OHLCVBar(
                asset=first_bar.asset,
                timeframe=target_timeframe,
                timestamp=chunk[0].timestamp if target_timeframe != Timeframe.D1 else bucket_ts,
                open=open_p,
                high=high_p,
                low=low_p,
                close=close_p,
                volume=total_vol,
                open_interest=last_oi,
                data_source=data_source,
            )
            aggregated.append(agg_bar)

        return aggregated

    @staticmethod
    def _round_tick(val: Decimal, tick_size: Decimal) -> Decimal:
        steps = (val / tick_size).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        return (steps * tick_size).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
