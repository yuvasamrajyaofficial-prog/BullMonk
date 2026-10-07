"""
Unit tests for Black-Scholes options pricing, Greeks, and delta-target strike selection.
"""

from __future__ import annotations

import math
import pytest

from core.enums import OptionType
from indicators.options import (
    BlackScholesGreeks,
    DeltaTargetOptionSelector,
    calculate_black_scholes,
)


class TestBlackScholesPricing:
    def test_call_pricing_benchmark(self):
        """
        Benchmark test:
        S = 100, K = 100, T = 1.0 year, vol = 0.20, r = 0.05
        Standard analytical textbook benchmark:
        d1 = (ln(1) + (0.05 + 0.02) * 1) / 0.20 = 0.07 / 0.20 = 0.35
        d2 = 0.35 - 0.20 = 0.15
        N(0.35) ~= 0.63683
        N(0.15) ~= 0.55962
        C ~= 100 * 0.63683 - 100 * exp(-0.05) * 0.55962 ~= 10.4506
        """
        greeks = calculate_black_scholes(
            spot=100.0,
            strike=100.0,
            time_to_expiry=1.0,
            volatility=0.20,
            risk_free_rate=0.05,
            option_type="call",
        )

        assert math.isclose(greeks.price, 10.4506, rel_tol=1e-3)
        assert math.isclose(greeks.delta, 0.6368, rel_tol=1e-3)
        assert greeks.gamma > 0.0
        assert greeks.theta_daily < 0.0  # Time decay is negative
        assert greeks.vega_1pct > 0.0  # Long option benefits from rising vol

    def test_put_pricing_and_put_call_parity(self):
        """
        Verify Put-Call Parity:
        C - P = S - K * exp(-r * T)
        """
        spot = 24000.0  # NIFTY spot
        strike = 24000.0
        t = 15.0 / 365.0  # 15 days
        vol = 0.14  # 14% India VIX
        r = 0.065  # 6.5% RBI repo rate

        call = calculate_black_scholes(spot, strike, t, vol, r, option_type="call")
        put = calculate_black_scholes(spot, strike, t, vol, r, option_type="put")

        # Put-Call Parity
        lhs = call.price - put.price
        rhs = spot - strike * math.exp(-r * t)
        assert math.isclose(lhs, rhs, rel_tol=1e-5, abs_tol=1e-4)

        # Delta relationship: Call Delta - Put Delta == 1.0
        assert math.isclose(call.delta - put.delta, 1.0, rel_tol=1e-5)

    def test_expired_option_edge_case(self):
        # T <= 0
        call_itm = calculate_black_scholes(spot=110.0, strike=100.0, time_to_expiry=0.0, volatility=0.2, option_type="call")
        assert call_itm.price == 10.0
        assert call_itm.delta == 1.0

        call_otm = calculate_black_scholes(spot=90.0, strike=100.0, time_to_expiry=0.0, volatility=0.2, option_type="call")
        assert call_otm.price == 0.0
        assert call_otm.delta == 0.0

        put_itm = calculate_black_scholes(spot=90.0, strike=100.0, time_to_expiry=0.0, volatility=0.2, option_type="put")
        assert put_itm.price == 10.0
        assert put_itm.delta == -1.0

    def test_zero_volatility_edge_case(self):
        # vol <= 0
        call = calculate_black_scholes(spot=120.0, strike=100.0, time_to_expiry=0.5, volatility=0.0, risk_free_rate=0.05, option_type="call")
        pv_strike = 100.0 * math.exp(-0.05 * 0.5)
        assert math.isclose(call.price, 120.0 - pv_strike, rel_tol=1e-5)

    def test_invalid_inputs(self):
        with pytest.raises(ValueError, match="strictly positive"):
            calculate_black_scholes(spot=-10.0, strike=100.0, time_to_expiry=1.0, volatility=0.2)
        with pytest.raises(ValueError, match="Unknown option_type"):
            calculate_black_scholes(spot=100.0, strike=100.0, time_to_expiry=1.0, volatility=0.2, option_type="invalid")


class TestDeltaTargetOptionSelector:
    def test_select_atm_call(self):
        strikes = [23800, 23900, 24000, 24100, 24200]
        res = DeltaTargetOptionSelector.select_strike(
            spot=24000.0,
            available_strikes=strikes,
            time_to_expiry_years=7.0 / 365.0,
            volatility=0.15,
            target_delta=0.50,
            option_type="call",
        )

        assert res.selected_strike == 24000.0
        assert math.isclose(res.actual_delta, 0.50, abs_tol=0.05)

    def test_select_deep_itm_call(self):
        strikes = [23000, 23500, 24000, 24500, 25000]
        res = DeltaTargetOptionSelector.select_strike(
            spot=24000.0,
            available_strikes=strikes,
            time_to_expiry_years=30.0 / 365.0,
            volatility=0.15,
            target_delta=0.85,
            option_type="call",
        )
        # Deep ITM call strike should be 23000 or 23500
        assert res.selected_strike in (23000, 23500)
        assert res.actual_delta > 0.70

    def test_select_atm_put(self):
        strikes = [23800, 23900, 24000, 24100, 24200]
        # Puts can be queried either with signed target (-0.50) or absolute magnitude (0.50)
        res = DeltaTargetOptionSelector.select_strike(
            spot=24000.0,
            available_strikes=strikes,
            time_to_expiry_years=7.0 / 365.0,
            volatility=0.15,
            target_delta=0.50,  # Absolute magnitude
            option_type="put",
        )
        assert res.selected_strike == 24000.0
        assert math.isclose(res.actual_delta, -0.50, abs_tol=0.05)
