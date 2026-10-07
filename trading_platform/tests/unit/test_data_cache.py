"""
Unit tests for the DataCache local Parquet storage layer.

Tests:
1. save() writes valid Parquet cache file.
2. exists() detects cached dataset.
3. load() returns identical bars with exact Decimal precision.
4. load() filters by start and end timestamps.
5. delete() removes file and updates manifest.
6. list() returns correct CacheMetadata identifying symbol, exchange, timeframe, and data_source.
7. Attempting to load non-existent cache raises FileNotFoundError.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from tempfile import mkdtemp

import pytest

from core.enums import DataSource, Timeframe
from core.models import OHLCVBar
from data.cache import DataCache
from data.nifty import create_nifty_index
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator


@pytest.fixture
def temp_cache_dir():
    d = mkdtemp()
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


@pytest.fixture
def sample_bars() -> list[OHLCVBar]:
    gen = SyntheticOHLCVGenerator(seed=42)
    return gen.generate(SyntheticDataConfig(number_of_sessions=2, timeframe=Timeframe.M5, seed=42))


class TestDataCache:

    def test_save_and_load_round_trip(self, temp_cache_dir: Path, sample_bars: list[OHLCVBar]):
        cache = DataCache(cache_dir=temp_cache_dir)
        asset = sample_bars[0].asset
        tf = sample_bars[0].timeframe

        assert cache.exists(asset, tf, DataSource.SYNTHETIC) is False

        saved_path = cache.save(asset, tf, sample_bars, data_source=DataSource.SYNTHETIC)
        assert Path(saved_path).exists()
        assert cache.exists(asset, tf, DataSource.SYNTHETIC) is True

        loaded_bars = cache.load(asset, tf, data_source=DataSource.SYNTHETIC)
        assert len(loaded_bars) == len(sample_bars)

        for orig, loaded in zip(sample_bars, loaded_bars):
            assert orig.timestamp == loaded.timestamp
            assert orig.open == loaded.open
            assert orig.high == loaded.high
            assert orig.low == loaded.low
            assert orig.close == loaded.close
            assert orig.volume == loaded.volume
            assert loaded.data_source == DataSource.SYNTHETIC

    def test_load_with_date_range_filtering(self, temp_cache_dir: Path, sample_bars: list[OHLCVBar]):
        cache = DataCache(cache_dir=temp_cache_dir)
        asset = sample_bars[0].asset
        tf = sample_bars[0].timeframe

        cache.save(asset, tf, sample_bars, data_source=DataSource.SYNTHETIC)

        # Slice between bar 10 and bar 20
        start_ts = sample_bars[10].timestamp
        end_ts = sample_bars[20].timestamp

        sliced_bars = cache.load(asset, tf, start=start_ts, end=end_ts, data_source=DataSource.SYNTHETIC)
        assert len(sliced_bars) == 11
        assert sliced_bars[0].timestamp == start_ts
        assert sliced_bars[-1].timestamp == end_ts

    def test_delete_removes_dataset(self, temp_cache_dir: Path, sample_bars: list[OHLCVBar]):
        cache = DataCache(cache_dir=temp_cache_dir)
        asset = sample_bars[0].asset
        tf = sample_bars[0].timeframe

        cache.save(asset, tf, sample_bars, data_source=DataSource.SYNTHETIC)
        assert cache.exists(asset, tf, DataSource.SYNTHETIC) is True

        res = cache.delete(asset, tf, DataSource.SYNTHETIC)
        assert res is True
        assert cache.exists(asset, tf, DataSource.SYNTHETIC) is False

    def test_list_cached_metadata(self, temp_cache_dir: Path, sample_bars: list[OHLCVBar]):
        cache = DataCache(cache_dir=temp_cache_dir)
        asset = sample_bars[0].asset
        tf = sample_bars[0].timeframe

        cache.save(asset, tf, sample_bars, data_source=DataSource.SYNTHETIC)
        meta_list = cache.list()

        assert len(meta_list) == 1
        meta = meta_list[0]
        assert meta.symbol == asset.symbol
        assert meta.exchange == asset.exchange.value
        assert meta.asset_class == asset.asset_class.value
        assert meta.timeframe == tf.value
        assert meta.data_source == DataSource.SYNTHETIC.value
        assert meta.bar_count == len(sample_bars)

    def test_load_non_existent_raises(self, temp_cache_dir: Path):
        cache = DataCache(cache_dir=temp_cache_dir)
        asset = create_nifty_index()
        with pytest.raises(FileNotFoundError):
            cache.load(asset, Timeframe.M1)
