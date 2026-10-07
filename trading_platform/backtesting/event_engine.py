"""
Event-Driven Backtesting Engine.

Coordinates the complete deterministic simulation lifecycle:
1. Historical Market Data Replay (no lookahead, chronological bars)
2. Strategy Signal Generation (`BaseStrategy.on_bar`)
3. Pre-Trade Risk Gatekeeping (`RiskManager.evaluate_order`)
4. Simulated Order Matching & Queue Execution (`SimulatedMatchingEngine`)
5. Transaction Cost and Slippage Models (`IndianMarketCostModel`)
6. Real-time Mark-to-Market Portfolio Accounting (`Portfolio`)
7. Advanced Institutional Analytics & Performance Tear Sheet (`AdvancedAnalyticsEngine`)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
import logging
from typing import Optional
import uuid

from analytics.advanced_metrics import AdvancedAnalyticsEngine, AdvancedMetricsResult
from backtesting.costs import CostModel, FixedBpsSlippageModel, IndianMarketCostModel, SlippageModel
from backtesting.matching_engine import SimulatedMatchingEngine
from core.clock import SimulatedClock
from core.enums import OrderStatus, OrderType, PositionSide, RiskDecisionType, Side, SignalType, Timeframe
from core.events import BarEvent, EventBus, OrderFilledEvent
from core.exceptions import InsufficientDataError
from core.models import Account, Asset, Balance, Fill, OHLCVBar, Order, PortfolioSnapshot, Position, RiskLimits, Signal, Trade
from data.interfaces import HistoricalDataProvider
from portfolio.portfolio import Portfolio
from risk.manager import RiskManager
from strategies.base import BaseStrategy

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DetailedBacktestResult:
    """Enriched backtest result containing metrics, trade log, and equity curve."""

    strategy_id: str
    asset: Asset
    timeframe: Timeframe
    start_date: datetime
    end_date: datetime
    bars_processed: int
    signals_generated: int
    orders_submitted: int
    orders_rejected: int
    fills_count: int
    metrics: AdvancedMetricsResult
    trades: list[Trade]
    snapshots: list[PortfolioSnapshot]
    fills: list[Fill]
    rejection_log: list[dict]


class EventDrivenBacktestEngine:
    """
    Production-grade event-driven quantitative backtesting engine.
    Ensures zero lookahead bias, strict tick/bar causality, and institutional accounting.
    """

    def __init__(
        self,
        data_provider: HistoricalDataProvider,
        initial_capital: Decimal = Decimal("1000000.0"),  # ₹10,00,000 INR
        cost_model: Optional[CostModel] = None,
        slippage_model: Optional[SlippageModel] = None,
        risk_limits: Optional[RiskLimits] = None,
        fill_on_next_open: bool = True,
        event_bus: Optional[EventBus] = None,
    ) -> None:
        self.data_provider = data_provider
        self.initial_capital = initial_capital
        self.cost_model = cost_model or IndianMarketCostModel()
        self.slippage_model = slippage_model or FixedBpsSlippageModel(basis_points=5.0)
        self.risk_limits = risk_limits or RiskLimits(
            max_daily_loss_pct=5.0,
            max_position_size_pct=25.0,
            max_open_positions=5,
        )
        self.fill_on_next_open = fill_on_next_open
        self.event_bus = event_bus or EventBus()
        self.analytics_engine = AdvancedAnalyticsEngine()

    def run(
        self,
        strategy: BaseStrategy,
        asset: Asset,
        timeframe: Timeframe,
        start: datetime,
        end: datetime,
        close_positions_at_end: bool = True,
    ) -> DetailedBacktestResult:
        """
        Execute the deterministic event-driven backtest.
        """
        logger.info(
            "EventDrivenBacktestEngine starting: strategy=%s asset=%s timeframe=%s",
            strategy.strategy_id, asset.symbol, timeframe.value,
        )

        bars = self.data_provider.get_bars(asset, timeframe, start, end)
        if not bars:
            raise InsufficientDataError(symbol=asset.symbol, required_bars=1, available_bars=0)

        # 1. Initialize Clock, Account, Portfolio
        clock = SimulatedClock(start_time=bars[0].timestamp)
        initial_balance = Balance(
            currency=asset.currency,
            available=self.initial_capital,
            total_equity=self.initial_capital,
        )
        account = Account(
            account_id="SIM-ACCOUNT-1",
            broker_name="SIMULATED-EXCHANGE",
            balances={asset.currency: initial_balance},
            is_live=False,
        )
        portfolio = Portfolio(account=account)

        # 2. Initialize Risk Manager & Matching Engine
        risk_manager = RiskManager(limits=self.risk_limits, event_bus=self.event_bus)
        matching_engine = SimulatedMatchingEngine(
            cost_model=self.cost_model,
            slippage_model=self.slippage_model,
            fill_on_next_open=self.fill_on_next_open,
        )

        # Tracking state
        cash_balance = self.initial_capital
        order_map: dict[str, Order] = {}
        completed_trades: list[Trade] = []
        snapshots: list[PortfolioSnapshot] = []
        rejection_log: list[dict] = []
        signals_count = 0
        orders_submitted = 0
        orders_rejected = 0

        # Trade tracking per position entry
        open_trade_entries: dict[str, list[dict]] = {}

        strategy.initialize()

        for idx, bar in enumerate(bars):
            clock.set_time(bar.timestamp)

            # ── Step A: Process pending & resting orders against current bar ──
            new_fills = matching_engine.process_bar(bar)
            for fill in new_fills:
                order = order_map.get(fill.order_id)
                if not order:
                    continue

                portfolio.process_fill(fill, order)

                # Cash accounting
                turnover = fill.price * fill.quantity
                if fill.side == Side.BUY:
                    cash_balance -= (turnover + fill.commission)
                else:
                    cash_balance += (turnover - fill.commission)

                # Round-trip trade matching for analytics
                sym = fill.asset.symbol
                if sym not in open_trade_entries:
                    open_trade_entries[sym] = []

                if fill.side == Side.BUY:
                    # Open Long or close Short
                    if open_trade_entries[sym] and open_trade_entries[sym][0]["side"] == Side.SELL:
                        # Closing short
                        entry = open_trade_entries[sym].pop(0)
                        qty = min(entry["qty"], fill.quantity)
                        gross_pnl = (entry["price"] - fill.price) * qty
                        total_comm = entry["commission"] + fill.commission
                        net_pnl = gross_pnl - total_comm
                        completed_trades.append(
                            Trade(
                                trade_id=f"TR-{uuid.uuid4().hex[:8].upper()}",
                                strategy_id=strategy.strategy_id,
                                asset=fill.asset,
                                side=Side.SELL,
                                entry_time=entry["time"],
                                exit_time=fill.timestamp,
                                entry_price=entry["price"],
                                exit_price=fill.price,
                                quantity=qty,
                                gross_pnl=gross_pnl,
                                commission=total_comm,
                                net_pnl=net_pnl,
                            )
                        )
                    else:
                        open_trade_entries[sym].append({
                            "side": Side.BUY, "price": fill.price, "qty": fill.quantity,
                            "time": fill.timestamp, "commission": fill.commission,
                        })
                else:
                    # SELL: Open Short or close Long
                    if open_trade_entries[sym] and open_trade_entries[sym][0]["side"] == Side.BUY:
                        # Closing long
                        entry = open_trade_entries[sym].pop(0)
                        qty = min(entry["qty"], fill.quantity)
                        gross_pnl = (fill.price - entry["price"]) * qty
                        total_comm = entry["commission"] + fill.commission
                        net_pnl = gross_pnl - total_comm
                        completed_trades.append(
                            Trade(
                                trade_id=f"TR-{uuid.uuid4().hex[:8].upper()}",
                                strategy_id=strategy.strategy_id,
                                asset=fill.asset,
                                side=Side.BUY,
                                entry_time=entry["time"],
                                exit_time=fill.timestamp,
                                entry_price=entry["price"],
                                exit_price=fill.price,
                                quantity=qty,
                                gross_pnl=gross_pnl,
                                commission=total_comm,
                                net_pnl=net_pnl,
                            )
                        )
                    else:
                        open_trade_entries[sym].append({
                            "side": Side.SELL, "price": fill.price, "qty": fill.quantity,
                            "time": fill.timestamp, "commission": fill.commission,
                        })

                self.event_bus.publish(
                    OrderFilledEvent(source="BacktestEngine", payload={"fill": fill.model_dump(mode="json")})
                )

            # ── Step B: Mark-to-Market at bar close ──
            portfolio.mark_to_market(asset.symbol, bar.close)
            pos = portfolio.get_position(asset.symbol)
            if pos and pos.quantity > Decimal("0"):
                if pos.side == PositionSide.LONG:
                    market_val = pos.quantity * bar.close
                elif pos.side == PositionSide.SHORT:
                    market_val = -(pos.quantity * bar.close)
                else:
                    market_val = Decimal("0")
            else:
                market_val = Decimal("0")
            current_equity = cash_balance + market_val

            # Update Account balance object
            balance = account.get_balance(asset.currency)
            if balance:
                account.balances[asset.currency] = Balance(
                    currency=asset.currency,
                    available=max(cash_balance, Decimal("0")),
                    total_equity=current_equity,
                )

            # Record periodic snapshot
            snapshot = PortfolioSnapshot(
                timestamp=bar.timestamp,
                account_id=account.account_id,
                positions=portfolio.get_open_positions(),
                total_equity=current_equity,
                total_unrealized_pnl=portfolio.get_total_unrealized_pnl(),
                total_realized_pnl=portfolio.get_total_realized_pnl(),
                cash_balance=cash_balance,
            )
            snapshots.append(snapshot)

            # ── Step C: Strategy processes bar and generates signals ──
            signals = strategy.on_bar(bar)
            if signals:
                signals_count += len(signals)
                for signal in signals:
                    strategy._emit_signal(signal)

                    # Translate signal to Order
                    order = self._signal_to_order(signal, bar, account)
                    if not order:
                        continue

                    # Pre-trade Risk Check
                    decision = risk_manager.evaluate_order(
                        order=order,
                        account=account,
                        open_positions=portfolio.get_open_positions(),
                    )

                    if decision.decision == RiskDecisionType.APPROVED:
                        orders_submitted += 1
                        order_map[order.order_id] = order
                        matching_engine.submit_order(order)
                    else:
                        orders_rejected += 1
                        rejection_log.append({
                            "time": bar.timestamp,
                            "order_id": order.order_id,
                            "reason": decision.reason,
                        })

        # Close remaining open position at last bar price if requested
        if close_positions_at_end and bars:
            last_bar = bars[-1]
            pos = portfolio.get_position(asset.symbol)
            if pos and pos.quantity > Decimal("0"):
                close_side = Side.SELL if pos.side == PositionSide.LONG else Side.BUY
                close_order = Order(
                    order_id=f"CLOSE-POS-{uuid.uuid4().hex[:6].upper()}",
                    asset=asset,
                    side=close_side,
                    order_type=OrderType.MARKET,
                    quantity=pos.quantity,
                    created_at=last_bar.timestamp,
                )
                matching_engine.submit_order(close_order)
                close_fills = matching_engine.process_bar(last_bar)
                for fill in close_fills:
                    portfolio.process_fill(fill, close_order)
                    turnover = fill.price * fill.quantity
                    if fill.side == Side.SELL:
                        cash_balance += (turnover - fill.commission)
                    else:
                        cash_balance -= (turnover + fill.commission)

        strategy.on_stop()

        # Compute full institutional analytics
        metrics = self.analytics_engine.compute_metrics(
            trades=completed_trades,
            equity_snapshots=snapshots,
            initial_capital=self.initial_capital,
        )

        return DetailedBacktestResult(
            strategy_id=strategy.strategy_id,
            asset=asset,
            timeframe=timeframe,
            start_date=start,
            end_date=end,
            bars_processed=len(bars),
            signals_generated=signals_count,
            orders_submitted=orders_submitted,
            orders_rejected=orders_rejected,
            fills_count=matching_engine.total_executed_fills,
            metrics=metrics,
            trades=completed_trades,
            snapshots=snapshots,
            fills=matching_engine._executed_fills,
            rejection_log=rejection_log,
        )

    def _signal_to_order(self, signal: Signal, bar: OHLCVBar, account: Account) -> Optional[Order]:
        """Convert a strategy signal into an actionable order."""
        if signal.signal_type == SignalType.NO_SIGNAL:
            return None

        # Determine side
        if signal.signal_type in (SignalType.ENTER_LONG, SignalType.EXIT_SHORT):
            side = Side.BUY
        elif signal.signal_type in (SignalType.ENTER_SHORT, SignalType.EXIT_LONG):
            side = Side.SELL
        else:
            return None

        # Determine quantity
        if signal.suggested_quantity and signal.suggested_quantity > Decimal("0"):
            qty = signal.suggested_quantity
        else:
            # Default sizing: 1 lot or 5% of equity
            bal = account.get_balance(signal.asset.currency)
            equity = bal.total_equity if bal else self.initial_capital
            target_value = equity * Decimal("0.05")
            qty = max(Decimal("1"), round(target_value / bar.close))

        return Order(
            order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            strategy_id=signal.strategy_id,
            asset=signal.asset,
            side=side,
            order_type=OrderType.MARKET,
            quantity=qty,
            created_at=bar.timestamp,
        )
