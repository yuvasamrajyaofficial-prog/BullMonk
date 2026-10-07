"""
Local market data cache with columnar Parquet storage.

Supports analytical workflows with:
- save()
- load()
- exists()
- delete()
- list()

Explicitly tracks:
- Symbol
- Exchange
- Asset class
- Timeframe
- Date range (start and end timestamps)
- Data source (REAL vs SYNTHETIC)
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

try:
    import pyarrow as pa
    import pyarrow.parquet as pq
    HAS_PYARROW = True
except ImportError:
    HAS_PYARROW = False

from core.enums import AssetClass, DataSource, Exchange, InstrumentType, Timeframe
from core.models import Asset, OHLCVBar


@dataclass(frozen=True)
class CacheMetadata:
    """Metadata describing a cached historical dataset."""

    symbol: str
    exchange: str
    asset_class: str
    timeframe: str
    start_date: str          # ISO 8601 UTC
    end_date: str            # ISO 8601 UTC
    data_source: str         # "REAL", "SYNTHETIC", etc.
    bar_count: int
    created_at: str
    file_path: str


class DataCache:
    """
    Columnar Parquet cache for historical OHLCV data.
    Falls back gracefully to JSON storage if PyArrow is not present.
    """

    def __init__(self, cache_dir: Optional[Path | str] = None) -> None:
        if cache_dir is None:
            # Default to local cache directory inside platform
            self.cache_dir = Path(__file__).resolve().parent / "cache_storage"
        else:
            self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.cache_dir / "_cache_manifest.json"
        self._manifest: dict[str, dict[str, Any]] = self._load_manifest()

    def _load_manifest(self) -> dict[str, dict[str, Any]]:
        if self.manifest_file.exists():
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_manifest(self) -> None:
        try:
            with open(self.manifest_file, "w", encoding="utf-8") as f:
                json.dump(self._manifest, f, indent=2)
        except Exception:
            pass

    def _build_key(
        self,
        asset: Asset,
        timeframe: Timeframe,
        data_source: DataSource,
    ) -> str:
        sym = asset.symbol.replace("/", "_").replace(" ", "_")
        return f"{sym}_{asset.exchange.value}_{asset.asset_class.value}_{timeframe.value}_{data_source.value}"

    def exists(
        self,
        asset: Asset,
        timeframe: Timeframe,
        data_source: Optional[DataSource] = None,
    ) -> bool:
        """Return True if cached data exists for the given asset, timeframe, and source."""
        sources = [data_source] if data_source is not None else [DataSource.REAL, DataSource.SYNTHETIC, DataSource.BACKTEST_SIMULATED]
        for s in sources:
            key = self._build_key(asset, timeframe, s)
            if key in self._manifest:
                file_path = Path(self._manifest[key]["file_path"])
                if file_path.exists():
                    return True
            parquet_path = self.cache_dir / f"{key}.parquet"
            json_path = self.cache_dir / f"{key}.json"
            if parquet_path.exists() or json_path.exists():
                return True
        return False

    def save(
        self,
        asset: Asset,
        timeframe: Timeframe,
        bars: list[OHLCVBar],
        data_source: Optional[DataSource] = None,
    ) -> str:
        """
        Save a collection of OHLCV bars to local storage.

        Args:
            asset: Asset associated with the data.
            timeframe: Timeframe of the bars.
            bars: List of OHLCVBar objects.
            data_source: Explicit source flag (defaults to bars[0].data_source or REAL).

        Returns:
            Absolute file path of the saved cache artifact.
        """
        if not bars:
            raise ValueError("Cannot save empty bar list to cache")

        source = data_source or bars[0].data_source
        key = self._build_key(asset, timeframe, source)

        sorted_bars = sorted(bars, key=lambda b: b.timestamp)
        start_ts = sorted_bars[0].timestamp.astimezone(timezone.utc).isoformat()
        end_ts = sorted_bars[-1].timestamp.astimezone(timezone.utc).isoformat()
        now_ts = datetime.now(tz=timezone.utc).isoformat()

        if HAS_PYARROW:
            target_path = self.cache_dir / f"{key}.parquet"
            # Build PyArrow Table
            timestamps = [b.timestamp.astimezone(timezone.utc) for b in sorted_bars]
            opens = [str(b.open) for b in sorted_bars]
            highs = [str(b.high) for b in sorted_bars]
            lows = [str(b.low) for b in sorted_bars]
            closes = [str(b.close) for b in sorted_bars]
            volumes = [str(b.volume) for b in sorted_bars]
            open_interests = [str(b.open_interest) if b.open_interest is not None else "" for b in sorted_bars]
            data_sources = [b.data_source.value for b in sorted_bars]

            table = pa.Table.from_arrays(
                [
                    pa.array(timestamps, pa.timestamp("us", tz="UTC")),
                    pa.array(opens, pa.string()),
                    pa.array(highs, pa.string()),
                    pa.array(lows, pa.string()),
                    pa.array(closes, pa.string()),
                    pa.array(volumes, pa.string()),
                    pa.array(open_interests, pa.string()),
                    pa.array(data_sources, pa.string()),
                ],
                names=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "open_interest",
                    "data_source",
                ],
            )
            pq.write_table(table, target_path, compression="snappy")
        else:
            target_path = self.cache_dir / f"{key}.json"
            data = [
                {
                    "timestamp": b.timestamp.astimezone(timezone.utc).isoformat(),
                    "open": str(b.open),
                    "high": str(b.high),
                    "low": str(b.low),
                    "close": str(b.close),
                    "volume": str(b.volume),
                    "open_interest": str(b.open_interest) if b.open_interest else None,
                    "data_source": b.data_source.value,
                }
                for b in sorted_bars
            ]
            with open(target_path, "w", encoding="utf-8") as f:
                json.dump(data, f)

        metadata_entry = {
            "symbol": asset.symbol,
            "exchange": asset.exchange.value,
            "asset_class": asset.asset_class.value,
            "timeframe": timeframe.value,
            "start_date": start_ts,
            "end_date": end_ts,
            "data_source": source.value,
            "bar_count": len(sorted_bars),
            "created_at": now_ts,
            "file_path": str(target_path),
        }
        self._manifest[key] = metadata_entry
        self._save_manifest()
        return str(target_path)

    def load(
        self,
        asset: Asset,
        timeframe: Timeframe,
        start: Optional[datetime] = None,
        end: Optional[datetime] = None,
        data_source: Optional[DataSource] = None,
    ) -> list[OHLCVBar]:
        """
        Load cached bars for asset, optionally filtering by date range.

        Args:
            asset: Target asset.
            timeframe: Target timeframe.
            start: Optional inclusive UTC start time.
            end: Optional inclusive UTC end time.
            data_source: Optional data source filter.

        Returns:
            List of OHLCVBar objects in ascending chronological order.
        """
        if data_source is not None:
            source = data_source
        else:
            source = DataSource.REAL
            for s in (DataSource.REAL, DataSource.SYNTHETIC, DataSource.BACKTEST_SIMULATED):
                if self.exists(asset, timeframe, s):
                    source = s
                    break

        key = self._build_key(asset, timeframe, source)
        parquet_path = self.cache_dir / f"{key}.parquet"
        json_path = self.cache_dir / f"{key}.json"

        bars: list[OHLCVBar] = []

        if parquet_path.exists() and HAS_PYARROW:
            table = pq.read_table(parquet_path)
            ts_col = table["timestamp"].to_pylist()
            open_col = table["open"].to_pylist()
            high_col = table["high"].to_pylist()
            low_col = table["low"].to_pylist()
            close_col = table["close"].to_pylist()
            vol_col = table["volume"].to_pylist()
            oi_col = table["open_interest"].to_pylist()
            source_col = table["data_source"].to_pylist()

            for i in range(len(ts_col)):
                ts = ts_col[i]
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                else:
                    ts = ts.astimezone(timezone.utc)

                if start and ts < start.astimezone(timezone.utc):
                    continue
                if end and ts > end.astimezone(timezone.utc):
                    continue

                oi_val = Decimal(oi_col[i]) if oi_col[i] else None
                bar = OHLCVBar(
                    asset=asset,
                    timeframe=timeframe,
                    timestamp=ts,
                    open=Decimal(open_col[i]),
                    high=Decimal(high_col[i]),
                    low=Decimal(low_col[i]),
                    close=Decimal(close_col[i]),
                    volume=Decimal(vol_col[i]),
                    open_interest=oi_val,
                    data_source=DataSource(source_col[i]),
                )
                bars.append(bar)

        elif json_path.exists():
            with open(json_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            for item in raw_data:
                ts = datetime.fromisoformat(item["timestamp"])
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                else:
                    ts = ts.astimezone(timezone.utc)

                if start and ts < start.astimezone(timezone.utc):
                    continue
                if end and ts > end.astimezone(timezone.utc):
                    continue

                oi_val = Decimal(item["open_interest"]) if item.get("open_interest") else None
                bar = OHLCVBar(
                    asset=asset,
                    timeframe=timeframe,
                    timestamp=ts,
                    open=Decimal(item["open"]),
                    high=Decimal(item["high"]),
                    low=Decimal(item["low"]),
                    close=Decimal(item["close"]),
                    volume=Decimal(item["volume"]),
                    open_interest=oi_val,
                    data_source=DataSource(item["data_source"]),
                )
                bars.append(bar)
        else:
            raise FileNotFoundError(f"No cached data found for key: {key}")

        bars.sort(key=lambda b: b.timestamp)
        return bars

    def delete(
        self,
        asset: Asset,
        timeframe: Timeframe,
        data_source: Optional[DataSource] = None,
    ) -> bool:
        """Delete cache file and manifest entry for given asset and timeframe."""
        source = data_source or DataSource.REAL
        key = self._build_key(asset, timeframe, source)
        deleted = False

        parquet_path = self.cache_dir / f"{key}.parquet"
        if parquet_path.exists():
            parquet_path.unlink()
            deleted = True

        json_path = self.cache_dir / f"{key}.json"
        if json_path.exists():
            json_path.unlink()
            deleted = True

        if key in self._manifest:
            del self._manifest[key]
            self._save_manifest()
            deleted = True

        return deleted

    def list(self) -> list[CacheMetadata]:
        """List metadata for all currently cached datasets."""
        results: list[CacheMetadata] = []
        for key, entry in self._manifest.items():
            results.append(
                CacheMetadata(
                    symbol=entry["symbol"],
                    exchange=entry["exchange"],
                    asset_class=entry["asset_class"],
                    timeframe=entry["timeframe"],
                    start_date=entry["start_date"],
                    end_date=entry["end_date"],
                    data_source=entry["data_source"],
                    bar_count=entry["bar_count"],
                    created_at=entry["created_at"],
                    file_path=entry["file_path"],
                )
            )
        return results

    def clear(self) -> int:
        """Remove all cached files and reset the manifest."""
        count = 0
        for p in self.cache_dir.glob("*.parquet"):
            p.unlink()
            count += 1
        for p in self.cache_dir.glob("*.json"):
            p.unlink()
            count += 1
        self._manifest.clear()
        self._save_manifest()
        return count
