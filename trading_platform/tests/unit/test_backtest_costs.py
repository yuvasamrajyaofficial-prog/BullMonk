from datetime import datetime, timezone
from decimal import Decimal
import pytest

from backtesting.costs import (
    FixedBpsSlippageModel,
    FlatPercentageCostModel,
    IndianMarketCostModel,
    VolumeShareSlippageModel,
    ZeroCostModel,
    ZeroSlippageModel,
)
from core.enums import AssetClass, Side
from data.nifty import create_nifty_future, create_nifty_index, create_nifty_option


class TestSlippageModels:
    def test_zero_slippage_model(self):
        model = ZeroSlippageModel()
        price = model.calculate_fill_price(
            target_price=Decimal("24500.00"),
            side=Side.BUY,
            quantity=Decimal("50"),
            bar_open=Decimal("24500.00"),
            bar_high=Decimal("24550.00"),
            bar_low=Decimal("24480.00"),
            bar_close=Decimal("24520.00"),
            bar_volume=50000,
        )
        assert price == Decimal("24500.00")

    def test_fixed_bps_slippage_model_buy_and_sell(self):
        model = FixedBpsSlippageModel(basis_points=10.0)  # 10 bps = 0.1%
        target = Decimal("1000.00")

        # Buy price slips UP
        buy_price = model.calculate_fill_price(
            target_price=target,
            side=Side.BUY,
            quantity=Decimal("10"),
            bar_open=target,
            bar_high=Decimal("1010.00"),
            bar_low=Decimal("990.00"),
            bar_close=target,
            bar_volume=1000,
        )
        assert buy_price == Decimal("1001.00")

        # Sell price slips DOWN
        sell_price = model.calculate_fill_price(
            target_price=target,
            side=Side.SELL,
            quantity=Decimal("10"),
            bar_open=target,
            bar_high=Decimal("1010.00"),
            bar_low=Decimal("990.00"),
            bar_close=target,
            bar_volume=1000,
        )
        assert sell_price == Decimal("999.00")

    def test_volume_share_slippage_clamping(self):
        model = VolumeShareSlippageModel(base_bps=5.0, impact_factor=0.2)
        # Large order relative to volume should be clamped to bar High
        buy_price = model.calculate_fill_price(
            target_price=Decimal("100.00"),
            side=Side.BUY,
            quantity=Decimal("10000"),
            bar_open=Decimal("100.00"),
            bar_high=Decimal("105.00"),
            bar_low=Decimal("95.00"),
            bar_close=Decimal("100.00"),
            bar_volume=100,  # Huge impact
        )
        assert buy_price <= Decimal("105.00")


class TestIndianMarketCostModel:
    def test_equity_delivery_buy_costs(self):
        cost_model = IndianMarketCostModel(flat_brokerage_per_order=Decimal("20.00"))
        equity = create_nifty_index()
        # Delivery Buy: STT 0.1%, Stamp duty 0.015%, Exchange fee 0.00345%, GST 18%
        cost = cost_model.calculate_cost(
            asset=equity,
            side=Side.BUY,
            quantity=Decimal("100"),
            fill_price=Decimal("1000.00"),  # Turnover = 100,000
            is_intraday=False,
        )
        assert cost.brokerage == Decimal("20.00")
        assert cost.stt_ctt == Decimal("100.00")  # 0.1% of 100k
        assert cost.stamp_duty == Decimal("15.00")  # 0.015% of 100k
        assert cost.total_cost > Decimal("135.00")

    def test_equity_intraday_stt_only_on_sell(self):
        cost_model = IndianMarketCostModel()
        equity = create_nifty_index()
        # Intraday BUY: STT should be 0
        buy_cost = cost_model.calculate_cost(
            asset=equity,
            side=Side.BUY,
            quantity=Decimal("100"),
            fill_price=Decimal("1000.00"),
            is_intraday=True,
        )
        assert buy_cost.stt_ctt == Decimal("0.00")

        # Intraday SELL: STT should be 0.025% (₹25 on 100k)
        sell_cost = cost_model.calculate_cost(
            asset=equity,
            side=Side.SELL,
            quantity=Decimal("100"),
            fill_price=Decimal("1000.00"),
            is_intraday=True,
        )
        assert sell_cost.stt_ctt == Decimal("25.00")

    def test_futures_costs(self):
        cost_model = IndianMarketCostModel()
        future = create_nifty_future(expiry=datetime(2025, 2, 27, 10, 0, tzinfo=timezone.utc))
        # Futures Buy: Stamp duty on buy (0.002%), no STT
        cost = cost_model.calculate_cost(
            asset=future,
            side=Side.BUY,
            quantity=Decimal("50"),
            fill_price=Decimal("24000.00"),  # Turnover 1,200,000
        )
        assert cost.stt_ctt == Decimal("0.00")
        assert cost.stamp_duty == Decimal("24.00")  # 0.002% of 1.2M

    def test_options_turnover_costs(self):
        cost_model = IndianMarketCostModel()
        from core.enums import OptionType
        option = create_nifty_option(
            strike=Decimal("24500"),
            option_type=OptionType.CALL,
            expiry=datetime(2025, 2, 27, 10, 0, tzinfo=timezone.utc),
        )
        # Option Sell: STT 0.0625% on premium turnover
        cost = cost_model.calculate_cost(
            asset=option,
            side=Side.SELL,
            quantity=Decimal("50"),
            fill_price=Decimal("200.00"),  # Premium turnover = 10,000
        )
        assert cost.stt_ctt == Decimal("6.25")
