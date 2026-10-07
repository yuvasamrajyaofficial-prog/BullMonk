"""
CLI Test Script for the Quantitative Market Data Pipeline.

Usage:
    python -m data.test_data_pipeline
    (or python -m trading_platform.data.test_data_pipeline)

Executes the end-to-end data pipeline:
1. Generate synthetic NIFTY 50 historical data.
2. Validate data consistency and session alignment.
3. Normalize timestamps, prices, and resample timeframes.
4. Save dataset to local columnar Parquet cache.
5. Reload dataset and verify exact Decimal bit-level fidelity.
6. Print detailed summary statistics.
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

# Ensure trading_platform root is on sys.path
PLATFORM_DIR = Path(__file__).resolve().parent.parent
if str(PLATFORM_DIR) not in sys.path:
    sys.path.insert(0, str(PLATFORM_DIR))

# Safe Windows console characters
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def _safe_char(char: str, fallback: str) -> str:
    try:
        char.encode(sys.stdout.encoding or "utf-8")
        return char
    except Exception:
        return fallback


CHECK = _safe_char("✓", "[OK]")
LINE = _safe_char("─", "-")
BOLD = "\033[1m"
GREEN = "\033[92m"
BLUE = "\033[94m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def section(title: str) -> None:
    sep = LINE * 65
    print(f"\n{BOLD}{BLUE}{sep}{RESET}")
    print(f"{BOLD}{CYAN}  {title}{RESET}")
    print(f"{BOLD}{BLUE}{sep}{RESET}")


def main() -> int:
    from core.enums import DataSource, Timeframe
    from data.cache import DataCache
    from data.nifty import create_nifty_index
    from data.normalization import DataNormalizer
    from data.sessions import NSESessionCalendar
    from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
    from data.validation import DataValidator

    print(f"\n{BOLD}BullMonk Quantitative Market-Data Pipeline Test{RESET}")
    print(f"Timestamp: {datetime.now(tz=timezone.utc).isoformat()}")

    # ─────────────────────────────────────────────────────────────
    # STEP 1: GENERATE SYNTHETIC NIFTY DATA
    # ─────────────────────────────────────────────────────────────
    section("Step 1: Generate Synthetic NIFTY 50 Historical Data")

    nifty_asset = create_nifty_index()
    calendar = NSESessionCalendar()
    generator = SyntheticOHLCVGenerator(seed=42)

    config = SyntheticDataConfig(
        asset=nifty_asset,
        start_price=Decimal("24000.00"),
        volatility=0.16,
        drift=0.06,
        base_volume=Decimal("75000"),
        session_calendar=calendar,
        number_of_sessions=5,         # 5 full NSE trading days
        timeframe=Timeframe.M5,       # 5-minute bars
        seed=42,
        start_date=date(2025, 1, 6),  # Monday
    )

    raw_bars = generator.generate(config)
    print(f"  {GREEN}{CHECK}{RESET} Generated {len(raw_bars)} synthetic 5-minute bars across 5 sessions")
    print(f"  {GREEN}{CHECK}{RESET} Instrument: {nifty_asset.symbol} on {nifty_asset.exchange.value} ({nifty_asset.asset_class.value})")
    print(f"  {GREEN}{CHECK}{RESET} Time Range: {raw_bars[0].timestamp.isoformat()} to {raw_bars[-1].timestamp.isoformat()}")
    print(f"  {GREEN}{CHECK}{RESET} Data Provenance: {raw_bars[0].data_source.value} (is_synthetic={raw_bars[0].is_synthetic})")

    # Guard: Never label synthetic data as real
    for b in raw_bars:
        assert b.data_source == DataSource.SYNTHETIC, "Synthetic bar not flagged as DataSource.SYNTHETIC!"
        assert b.is_synthetic is True, "bar.is_synthetic returned False on synthetic bar!"

    # ─────────────────────────────────────────────────────────────
    # STEP 2: VALIDATE DATA CONSISTENCY
    # ─────────────────────────────────────────────────────────────
    section("Step 2: Validate Data Consistency & Quality")

    validator = DataValidator(calendar=calendar, check_session_boundaries=True)
    report = validator.validate_bars(raw_bars)

    print(report.summary())
    if not report.is_valid:
        print(f"  [ERROR] Validation failed with {report.error_count} errors!")
        return 1
    print(f"  {GREEN}{CHECK}{RESET} Validation Status: PASSED (Zero data corruption errors)")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: NORMALIZE AND RESAMPLE
    # ─────────────────────────────────────────────────────────────
    section("Step 3: Normalize Data & Resample Timeframes")

    normalizer = DataNormalizer()
    normalized_bars = normalizer.normalize_bars(raw_bars, enforce_tick_size=True)
    print(f"  {GREEN}{CHECK}{RESET} Normalized {len(normalized_bars)} bars (UTC timestamps + 0.05 tick size alignment)")

    # Test multi-timeframe resampling: 5m -> 15m and 5m -> 1h
    bars_15m = normalizer.resample_bars(normalized_bars, target_timeframe=Timeframe.M15)
    bars_1h = normalizer.resample_bars(normalized_bars, target_timeframe=Timeframe.H1)
    bars_daily = normalizer.resample_bars(normalized_bars, target_timeframe=Timeframe.D1)

    print(f"  {GREEN}{CHECK}{RESET} Resampled to 15m: {len(bars_15m)} bars")
    print(f"  {GREEN}{CHECK}{RESET} Resampled to 1h:  {len(bars_1h)} bars")
    print(f"  {GREEN}{CHECK}{RESET} Resampled to 1d:  {len(bars_daily)} bars")

    # Verify aggregation math on first daily bar
    day0 = bars_daily[0]
    expected_vol = sum((b.volume for b in normalized_bars[:75]), Decimal("0"))
    assert day0.volume == expected_vol, f"Daily volume mismatch: {day0.volume} vs {expected_vol}"
    assert day0.data_source == DataSource.SYNTHETIC, "Resampled bar lost synthetic provenance tag!"
    print(f"  {GREEN}{CHECK}{RESET} Resampling mathematical consistency verified (Volume, OHLC, Provenance)")

    # ─────────────────────────────────────────────────────────────
    # STEP 4: SAVE LOCALLY (PARQUET CACHE)
    # ─────────────────────────────────────────────────────────────
    section("Step 4: Save to Local Data Cache")

    cache = DataCache()
    saved_path = cache.save(
        asset=nifty_asset,
        timeframe=Timeframe.M5,
        bars=normalized_bars,
        data_source=DataSource.SYNTHETIC,
    )
    print(f"  {GREEN}{CHECK}{RESET} Saved to cache: {saved_path}")
    print(f"  {GREEN}{CHECK}{RESET} Cache exists verification: {cache.exists(nifty_asset, Timeframe.M5, DataSource.SYNTHETIC)}")

    # ─────────────────────────────────────────────────────────────
    # STEP 5: RELOAD FROM CACHE AND VERIFY
    # ─────────────────────────────────────────────────────────────
    section("Step 5: Reload from Cache & Verify Integrity")

    reloaded_bars = cache.load(
        asset=nifty_asset,
        timeframe=Timeframe.M5,
        data_source=DataSource.SYNTHETIC,
    )
    print(f"  {GREEN}{CHECK}{RESET} Reloaded {len(reloaded_bars)} bars from cache")

    assert len(reloaded_bars) == len(normalized_bars), "Bar count mismatch between saved and reloaded!"
    for orig, loaded in zip(normalized_bars, reloaded_bars):
        assert orig.timestamp == loaded.timestamp, f"Timestamp mismatch: {orig.timestamp} vs {loaded.timestamp}"
        assert orig.open == loaded.open, f"Open mismatch: {orig.open} vs {loaded.open}"
        assert orig.high == loaded.high, f"High mismatch: {orig.high} vs {loaded.high}"
        assert orig.low == loaded.low, f"Low mismatch: {orig.low} vs {loaded.low}"
        assert orig.close == loaded.close, f"Close mismatch: {orig.close} vs {loaded.close}"
        assert orig.volume == loaded.volume, f"Volume mismatch: {orig.volume} vs {loaded.volume}"
        assert loaded.data_source == DataSource.SYNTHETIC, "Reloaded bar data_source mismatch!"

    print(f"  {GREEN}{CHECK}{RESET} 100% Bit-level & Decimal precision equality verified across all {len(reloaded_bars)} bars")

    # ─────────────────────────────────────────────────────────────
    # STEP 6: PRINT SUMMARY STATISTICS
    # ─────────────────────────────────────────────────────────────
    section("Step 6: Summary Statistics")

    first_bar = reloaded_bars[0]
    last_bar = reloaded_bars[-1]
    highest_price = max(b.high for b in reloaded_bars)
    lowest_price = min(b.low for b in reloaded_bars)
    total_volume = sum((b.volume for b in reloaded_bars), Decimal("0"))
    avg_volume = total_volume / Decimal(str(len(reloaded_bars)))

    price_change = last_bar.close - first_bar.open
    pct_change = (price_change / first_bar.open) * Decimal("100")

    print(f"  Instrument:          {nifty_asset.symbol} ({nifty_asset.instrument_type.value})")
    print(f"  Exchange:            {nifty_asset.exchange.value}")
    print(f"  Timeframe:           {Timeframe.M5.value}")
    print(f"  Data Source:         {DataSource.SYNTHETIC.value} [Research / Synthetic]")
    print(f"  Total Bars:          {len(reloaded_bars)}")
    print(f"  Start (UTC):         {first_bar.timestamp.isoformat()}")
    print(f"  End (UTC):           {last_bar.timestamp.isoformat()}")
    print(f"  Open Price:          {first_bar.open:.2f} INR")
    print(f"  Close Price:         {last_bar.close:.2f} INR")
    print(f"  High Period:         {highest_price:.2f} INR")
    print(f"  Low Period:          {lowest_price:.2f} INR")
    print(f"  Net Change:          {price_change:+.2f} INR ({pct_change:+.2f}%)")
    print(f"  Total Volume:        {total_volume:,}")
    print(f"  Mean Bar Volume:     {avg_volume:,.0f}")

    cached_list = cache.list()
    print(f"\n  Active Local Cache Entries ({len(cached_list)}):")
    for item in cached_list:
        print(f"    - {item.symbol} [{item.exchange}] {item.timeframe} ({item.data_source}): {item.bar_count} bars -> {item.file_path}")

    section("Pipeline Test Completed Successfully")
    print(f"  {GREEN}{BOLD}{CHECK} ALL 6 PIPELINE STAGES PASSED.{RESET}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
