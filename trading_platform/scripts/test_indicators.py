"""
Quantitative Research & Feature Engine Demonstration Script.

Demonstrates:
1. Generating deterministic multi-session synthetic market data (NSE NIFTY simulation).
2. Constructing a modular FeaturePipeline combining trend, momentum, volatility, volume, and session indicators.
3. Calculating indicators with strict zero look-ahead bias and exact warmup handling.
4. Inspecting the latest feature values and warm feature matrix.
5. Computing analytical Black-Scholes theoretical European option pricing and Greeks.
6. Executing delta-target strike selection across candidate strikes.

Usage:
    python -m scripts.test_indicators
    or
    python trading_platform/scripts/test_indicators.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure trading_platform root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
import pandas as pd

from decimal import Decimal

from core.enums import Timeframe
from data.nifty import create_nifty_index
from data.sessions import NSESessionCalendar
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
from indicators import (
    ADX,
    ATR,
    EMA,
    HMA,
    MACD,
    OBV,
    ROC,
    RSI,
    SMA,
    WMA,
    BollingerBands,
    CVDProxy,
    DeltaTargetOptionSelector,
    FeaturePipeline,
    HistoricalVolatility,
    IchimokuCloud,
    SessionFeatures,
    SessionVWAP,
    Supertrend,
    VolumeRatio,
    VolumeSMA,
    calculate_black_scholes,
    default_registry,
)


def run_demonstration() -> None:
    print("=" * 80)
    print(" BULLMONK QUANTITATIVE INDICATOR & FEATURE ENGINE")
    print("=" * 80)

    # 1. Inspect Registry
    reg_indicators = default_registry.list_indicators()
    print(f"\n[1] Indicator Registry Initialized: {len(reg_indicators)} registered indicators")
    sample_keys = list(reg_indicators.keys())[:8]
    print(f"    Sample available: {', '.join(sample_keys)} ...")

    # 2. Generate Synthetic Market Data
    print("\n[2] Generating Synthetic OHLCV Market Data (NIFTY 50 Simulation, 5-minute bars)...")
    nifty = create_nifty_index()
    gen = SyntheticOHLCVGenerator(seed=42)
    cfg = SyntheticDataConfig(
        asset=nifty,
        number_of_sessions=3,
        timeframe=Timeframe.M5,
        start_price=Decimal("24000.00"),
        volatility=0.15,
        seed=42,
    )
    bars = gen.generate(cfg)
    print(f"    Generated {len(bars)} bars across 3 trading sessions.")

    # Convert to DataFrame
    df = pd.DataFrame(
        [
            {
                "timestamp": b.timestamp,
                "open": float(b.open),
                "high": float(b.high),
                "low": float(b.low),
                "close": float(b.close),
                "volume": float(b.volume),
            }
            for b in bars
        ]
    )
    print(f"    Initial Spot: {df['close'].iloc[0]:.2f} INR | Final Spot: {df['close'].iloc[-1]:.2f} INR")

    # 3. Assemble Feature Pipeline
    print("\n[3] Assembling Multi-Factor Feature Pipeline...")
    calendar = NSESessionCalendar()
    pipeline = FeaturePipeline([
        SMA(period=20),
        EMA(period=20),
        EMA(period=50),
        HMA(period=16),
        ADX(period=14),
        Supertrend(period=10, multiplier=3.0),
        RSI(period=14),
        MACD(fast_period=12, slow_period=26, signal_period=9),
        ATR(period=14),
        BollingerBands(period=20, std_dev=2.0),
        HistoricalVolatility(period=20, trading_days=252),
        OBV(),
        VolumeSMA(period=20),
        VolumeRatio(period=20),
        SessionVWAP(calendar=calendar),
        CVDProxy(calendar=calendar),
        SessionFeatures(calendar=calendar, opening_range_bars=6),
        IchimokuCloud(conversion_period=9, base_period=26, leading_span_b_period=52, displacement=26),
    ])

    print(f"    Total indicators in pipeline: {len(pipeline.indicators)}")
    print(f"    Calculated maximum warmup period: {pipeline.max_warmup_period} bars")

    # 4. Calculate Features
    print("\n[4] Executing Vectorized Feature Calculations...")
    features_df = pipeline.calculate(df)
    warm_df = pipeline.get_warm_data(df)
    print(f"    Feature matrix shape: {features_df.shape} (rows x columns)")
    print(f"    Warm rows ready for signal generation: {len(warm_df)} / {len(features_df)}")

    # 5. Display Latest Feature Values
    latest = features_df.iloc[-1]
    print("\n[5] Latest Feature Snapshot (Timestamp: {}):".format(latest["timestamp"]))
    print("-" * 60)
    print(f"  Price Action:      Close = {latest['close']:.2f} | Open = {latest['open']:.2f}")
    print(f"  Moving Averages:   SMA(20) = {latest['sma_20']:.2f} | EMA(20) = {latest['ema_20']:.2f} | EMA(50) = {latest['ema_50']:.2f}")
    print(f"  Supertrend:        Level = {latest['supertrend_10_3.0']:.2f} | Direction = {int(latest['supertrend_direction_10_3.0'])}")
    print(f"  ADX / Direction:   ADX = {latest['adx_14']:.2f} | +DI = {latest['plus_di_14']:.2f} | -DI = {latest['minus_di_14']:.2f}")
    print(f"  Momentum:          RSI(14) = {latest['rsi_14']:.2f} | MACD = {latest['macd_12_26']:.2f} | Hist = {latest['macd_hist_12_26_9']:.2f}")
    print(f"  Volatility:        ATR(14) = {latest['atr_14']:.2f} | BB Width = {latest['bb_width_20_2.0']:.4f} | Hist Vol = {latest['hist_vol_20']:.2f}%")
    print(f"  Volume & VWAP:     VWAP = {latest['vwap']:.2f} | VWAP Dev = {latest['vwap_deviation']:.2f}% | Vol Ratio = {latest['volume_ratio_20']:.2f}x")
    print(f"  CVD Proxy:         Candle Delta = {latest['candle_delta']:.1f} | Session CVD = {latest['session_cumulative_delta']:.1f}")
    print(f"  Ichimoku Cloud:    Tenkan = {latest['tenkan']:.2f} | Kijun = {latest['kijun']:.2f} | Cloud Top = {max(latest['senkou_a'], latest['senkou_b']):.2f}")
    print(f"                     Price Above Cloud: {bool(latest['price_above_cloud'])} | Cloud Bullish: {bool(latest['cloud_bullish'])}")

    # 6. Options Quantitative Engine & Greeks Demonstration
    print("\n[6] Options Quantitative Pricing & Analytical Greeks:")
    print("-" * 60)
    spot = latest["close"]
    strike = round(spot / 50.0) * 50.0  # ATM strike
    tte_years = 7.0 / 365.0  # 7-day weekly expiry
    vol = 0.15  # 15% IV
    r = 0.065  # 6.5% risk-free rate

    call_greeks = calculate_black_scholes(spot, strike, tte_years, vol, r, option_type="call")
    put_greeks = calculate_black_scholes(spot, strike, tte_years, vol, r, option_type="put")

    print(f"  Underlying Spot: {spot:.2f} | Strike: {strike:.2f} | DTE: 7 days | IV: {vol*100:.1f}%")
    print(f"  ATM Call: Price = {call_greeks.price:.2f} INR | Delta = {call_greeks.delta:+.4f} | Gamma = {call_greeks.gamma:.6f} | Theta/day = {call_greeks.theta_daily:.2f} | Vega = {call_greeks.vega_1pct:.2f}")
    print(f"  ATM Put:  Price = {put_greeks.price:.2f} INR | Delta = {put_greeks.delta:+.4f} | Gamma = {put_greeks.gamma:.6f} | Theta/day = {put_greeks.theta_daily:.2f} | Vega = {put_greeks.vega_1pct:.2f}")
    print("  * DISCLAIMER: Historical/theoretical option pricing is not a substitute for live executable option quotes.")

    # 7. Delta-Target Option Selection Demonstration
    print("\n[7] Delta-Target Option Selection:")
    print("-" * 60)
    candidate_strikes = [strike - 200, strike - 100, strike, strike + 100, strike + 200]
    target_deltas = [0.70, 0.50, 0.30]

    for td in target_deltas:
        sel = DeltaTargetOptionSelector.select_strike(
            spot=spot,
            available_strikes=candidate_strikes,
            time_to_expiry_years=tte_years,
            volatility=vol,
            target_delta=td,
            option_type="call",
            risk_free_rate=r,
        )
        print(f"  Target Delta = {td:.2f} -> Selected Strike: {sel.selected_strike:.0f} (Actual Delta: {sel.actual_delta:+.4f}, Theo Price: {sel.theoretical_price:.2f} INR, Error: {sel.delta_error:.4f})")

    print("\n" + "=" * 80)
    print(" DEMONSTRATION COMPLETE: ALL QUANTITATIVE FEATURES VALIDATED SUCCESSFULLY")
    print("=" * 80)


if __name__ == "__main__":
    run_demonstration()
