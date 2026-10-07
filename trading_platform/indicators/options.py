"""
Options quantitative pricing, Greeks, and strike selection module.

Implements:
- Numerically stable Black-Scholes theoretical pricing for European-style options
- Full Greeks: Delta, Gamma, Theta (daily and annual), Vega (1% vol step and annual)
- Robust edge-case handling (expired contracts T<=0, zero volatility sigma<=0, boundary strikes)
- Delta-Target Strike Selection helper for quantitative strike picking

CRITICAL ARCHITECTURAL REQUIREMENT:
Historical/theoretical option pricing is not a substitute for live executable option quotes.
This module is strictly intended for research, risk scenario analysis, strike selection,
and Greeks computation. Live trading and execution must always rely on actual market quotes.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Optional, Sequence, Union
import numpy as np
import pandas as pd

from core.enums import OptionType


@dataclass(frozen=True)
class BlackScholesGreeks:
    """
    Theoretical Black-Scholes European option pricing and Greeks output.
    """

    price: float
    delta: float
    gamma: float
    theta_daily: float
    theta_annual: float
    vega_1pct: float
    vega_annual: float

    # Aliases
    @property
    def theta(self) -> float:
        """Theta per calendar day (1/365 of annualized decay)."""
        return self.theta_daily

    @property
    def vega(self) -> float:
        """Vega per 1% absolute change in volatility."""
        return self.vega_1pct


@dataclass(frozen=True)
class StrikeSelectionResult:
    """
    Result of a delta-targeted option strike search.
    """

    selected_strike: float
    target_delta: float
    actual_delta: float
    delta_error: float
    option_type: str
    spot: float
    time_to_expiry_years: float
    volatility: float
    theoretical_price: float
    greeks: BlackScholesGreeks
    all_evaluated: list[dict[str, Any]] = field(default_factory=list)


def _norm_cdf(x: float) -> float:
    """Standard normal cumulative distribution function (CDF) via math.erf."""
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _norm_pdf(x: float) -> float:
    """Standard normal probability density function (PDF)."""
    return (1.0 / math.sqrt(2.0 * math.pi)) * math.exp(-0.5 * x * x)


def calculate_black_scholes(
    spot: float,
    strike: float,
    time_to_expiry: float,
    volatility: float,
    risk_free_rate: float = 0.06,
    option_type: Union[OptionType, str] = "call",
) -> BlackScholesGreeks:
    """
    Calculate theoretical European option price and analytical Greeks via Black-Scholes.

    Args:
        spot: Underlying asset spot price (must be > 0).
        strike: Option strike price (must be > 0).
        time_to_expiry: Time to expiration in years (e.g. 30 days = 30 / 365.0).
        volatility: Annualized implied or historical volatility (e.g. 0.20 for 20%).
        risk_free_rate: Annualized continuously-compounded risk-free rate (e.g. 0.06 for 6%).
        option_type: 'call'/'ce' or 'put'/'pe' (case-insensitive).

    Returns:
        BlackScholesGreeks containing price, delta, gamma, theta, vega.
    """
    if spot <= 0 or strike <= 0:
        raise ValueError(f"Spot ({spot}) and strike ({strike}) must be strictly positive")

    opt_str = (
        option_type.value.lower()
        if isinstance(option_type, OptionType)
        else str(option_type).lower()
    )
    is_call = opt_str in ("call", "ce")
    is_put = opt_str in ("put", "pe")

    if not (is_call or is_put):
        raise ValueError(f"Unknown option_type '{option_type}'. Expected 'call' or 'put'.")

    # Edge Case 1: Expired contract (T <= 0)
    if time_to_expiry <= 1e-12:
        if is_call:
            intrinsic = max(0.0, spot - strike)
            delta = 1.0 if spot > strike else (0.5 if spot == strike else 0.0)
        else:
            intrinsic = max(0.0, strike - spot)
            delta = -1.0 if spot < strike else (-0.5 if spot == strike else 0.0)

        return BlackScholesGreeks(
            price=intrinsic,
            delta=delta,
            gamma=0.0,
            theta_daily=0.0,
            theta_annual=0.0,
            vega_1pct=0.0,
            vega_annual=0.0,
        )

    # Edge Case 2: Zero or negative volatility
    if volatility <= 1e-12:
        discount = math.exp(-risk_free_rate * time_to_expiry)
        pv_strike = strike * discount
        if is_call:
            intrinsic = max(0.0, spot - pv_strike)
            delta = 1.0 if spot > pv_strike else 0.0
        else:
            intrinsic = max(0.0, pv_strike - spot)
            delta = -1.0 if spot < pv_strike else 0.0

        return BlackScholesGreeks(
            price=intrinsic,
            delta=delta,
            gamma=0.0,
            theta_daily=0.0,
            theta_annual=0.0,
            vega_1pct=0.0,
            vega_annual=0.0,
        )

    # Standard Numerically Stable Black-Scholes
    t = float(time_to_expiry)
    s = float(spot)
    k = float(strike)
    sigma = float(volatility)
    r = float(risk_free_rate)

    sqrt_t = math.sqrt(t)
    vol_sqrt_t = sigma * sqrt_t

    d1 = (math.log(s / k) + (r + 0.5 * sigma * sigma) * t) / vol_sqrt_t
    d2 = d1 - vol_sqrt_t

    cdf_d1 = _norm_cdf(d1)
    cdf_d2 = _norm_cdf(d2)
    pdf_d1 = _norm_pdf(d1)
    discount = math.exp(-r * t)

    gamma = pdf_d1 / (s * vol_sqrt_t)
    vega_annual = s * pdf_d1 * sqrt_t
    vega_1pct = vega_annual / 100.0

    if is_call:
        price = s * cdf_d1 - k * discount * cdf_d2
        delta = cdf_d1
        theta_annual = -(s * pdf_d1 * sigma) / (2.0 * sqrt_t) - r * k * discount * cdf_d2
    else:
        cdf_neg_d1 = _norm_cdf(-d1)
        cdf_neg_d2 = _norm_cdf(-d2)
        price = k * discount * cdf_neg_d2 - s * cdf_neg_d1
        delta = cdf_d1 - 1.0
        theta_annual = -(s * pdf_d1 * sigma) / (2.0 * sqrt_t) + r * k * discount * cdf_neg_d2

    theta_daily = theta_annual / 365.0

    # Ensure price does not violate non-negativity due to float rounding
    price = max(0.0, price)

    return BlackScholesGreeks(
        price=price,
        delta=delta,
        gamma=gamma,
        theta_daily=theta_daily,
        theta_annual=theta_annual,
        vega_1pct=vega_1pct,
        vega_annual=vega_annual,
    )


class DeltaTargetOptionSelector:
    """
    Identifies the option strike closest to a target theoretical delta from
    a set of candidate strikes.

    Supports:
    - Calls and Puts
    - Any underlying asset (NIFTY, BankNIFTY, Equities, Crypto, Forex)
    - Any expiration timeframe
    - Flexible delta formatting (signed or absolute magnitude)
    """

    @staticmethod
    def select_strike(
        spot: float,
        available_strikes: Sequence[Union[float, int, Decimal]],
        time_to_expiry_years: float,
        volatility: float,
        target_delta: float,
        option_type: Union[OptionType, str] = "call",
        risk_free_rate: float = 0.06,
    ) -> StrikeSelectionResult:
        """
        Evaluate candidate strikes and select the closest match to `target_delta`.

        Args:
            spot: Current spot price.
            available_strikes: Sequence of available candidate strike prices.
            time_to_expiry_years: Time to expiration in years.
            volatility: Annualized volatility (e.g. 0.18 for 18%).
            target_delta: Target delta (e.g. 0.50 for ATM call, -0.50 or 0.50 for ATM put, 0.75 for ITM call).
            option_type: 'call' or 'put'.
            risk_free_rate: Annualized risk-free rate.

        Returns:
            StrikeSelectionResult containing the best strike and associated Greeks.
        """
        if not available_strikes:
            raise ValueError("available_strikes cannot be empty")

        opt_str = (
            option_type.value.lower()
            if isinstance(option_type, OptionType)
            else str(option_type).lower()
        )
        is_call = opt_str in ("call", "ce")

        # Normalize target delta for puts if user supplied positive magnitude (e.g. 0.50 for put)
        target = float(target_delta)
        if not is_call and target > 0:
            target = -target

        evaluated = []
        best_strike = None
        best_diff = float("inf")
        best_greeks = None

        for k_val in available_strikes:
            strike = float(k_val)
            greeks = calculate_black_scholes(
                spot=spot,
                strike=strike,
                time_to_expiry=time_to_expiry_years,
                volatility=volatility,
                risk_free_rate=risk_free_rate,
                option_type=opt_str,
            )

            diff = abs(greeks.delta - target)
            evaluated.append(
                {
                    "strike": strike,
                    "delta": greeks.delta,
                    "diff": diff,
                    "price": greeks.price,
                    "gamma": greeks.gamma,
                    "theta": greeks.theta_daily,
                    "vega": greeks.vega_1pct,
                }
            )

            if diff < best_diff:
                best_diff = diff
                best_strike = strike
                best_greeks = greeks

        assert best_strike is not None and best_greeks is not None

        return StrikeSelectionResult(
            selected_strike=best_strike,
            target_delta=target,
            actual_delta=best_greeks.delta,
            delta_error=best_diff,
            option_type="call" if is_call else "put",
            spot=spot,
            time_to_expiry_years=time_to_expiry_years,
            volatility=volatility,
            theoretical_price=best_greeks.price,
            greeks=best_greeks,
            all_evaluated=evaluated,
        )
