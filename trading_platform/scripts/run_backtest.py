"""
BullMonk Quantitative Platform — CLI Backtest Runner.

Executes an end-to-end backtest on NIFTY 50 data, prints an institutional
ASCII tear-sheet, and audits trade executions and risk limits.

Usage:
    python -m scripts.run_backtest --strategy dual_ema --timeframe 15m
    python -m scripts.run_backtest --strategy orb --timeframe 5m
    python -m scripts.run_backtest --strategy bollinger --timeframe 15m
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from decimal import Decimal
import sys

from analytics.tearsheet import TearSheetFormatter
from backtesting.costs import IndianMarketCostModel, FixedBpsSlippageModel
from backtesting.event_engine import EventDrivenBacktestEngine
from core.enums import Timeframe
from data.nifty import create_nifty_index
from data.providers.synthetic_provider import SyntheticHistoricalProvider
from strategies.library import DualEMAStrategy, OpeningRangeBreakoutStrategy, BollingerReversionStrategy


def run_cli_backtest(strategy_name: str = "dual_ema", timeframe_str: str = "15m", days: int = 30) -> int:
    tf_map = {
        "1m": Timeframe.M1,
        "5m": Timeframe.M5,
        "15m": Timeframe.M15,
        "1h": Timeframe.H1,
        "1d": Timeframe.D1,
    }
    tf = tf_map.get(timeframe_str.lower(), Timeframe.M15)
    nifty_asset = create_nifty_index()

    # 1. Setup deterministic synthetic NIFTY 50 market data
    data_provider = SyntheticHistoricalProvider(
        seed=42,
        volatility=0.16,
        drift=0.05,
    )

    start = datetime(2025, 1, 1, 3, 45, tzinfo=timezone.utc)  # 09:15 IST
    end = datetime(2025, 1, 30, 10, 0, tzinfo=timezone.utc)   # 15:30 IST

    # 2. Select strategy
    if strategy_name.lower() == "orb":
        strategy = OpeningRangeBreakoutStrategy(trade_quantity=Decimal("50"))
    elif strategy_name.lower() == "bollinger":
        strategy = BollingerReversionStrategy(trade_quantity=Decimal("50"))
    else:
        strategy = DualEMAStrategy(fast_period=9, slow_period=21, trade_quantity=Decimal("50"))

    # 3. Instantiate Engine
    engine = EventDrivenBacktestEngine(
        data_provider=data_provider,
        initial_capital=Decimal("1000000.00"),  # ₹10,00,000 INR
        cost_model=IndianMarketCostModel(flat_brokerage_per_order=Decimal("20.0")),
        slippage_model=FixedBpsSlippageModel(basis_points=5.0),
        fill_on_next_open=True,
    )

    print(f"\n[BullMonk Backtest] Running {strategy.strategy_id} on {nifty_asset.symbol} ({tf.value})...")
    result = engine.run(
        strategy=strategy,
        asset=nifty_asset,
        timeframe=tf,
        start=start,
        end=end,
    )

    # 4. Print Tear Sheet
    report = TearSheetFormatter.format_terminal_report(
        metrics=result.metrics,
        strategy_id=result.strategy_id,
        symbol=nifty_asset.symbol,
    )
    print(report)

    print(f"[OK] Backtest complete: {result.bars_processed} bars processed, {result.metrics.total_trades} trades executed.\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BullMonk Quantitative Backtester CLI")
    parser.add_argument("--strategy", default="dual_ema", choices=["dual_ema", "orb", "bollinger"])
    parser.add_argument("--timeframe", default="15m", choices=["1m", "5m", "15m", "1h", "1d"])
    args = parser.parse_args()

    sys.exit(run_cli_backtest(strategy_name=args.strategy, timeframe_str=args.timeframe))
