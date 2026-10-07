"""
Unit tests for NIFTY 50 concrete domain models, factories, and option chain metadata.

Tests:
1. create_nifty_index() creates valid NSE equity index asset.
2. create_nifty_future() creates valid NFO index futures with lot size and expiry.
3. create_nifty_option() creates valid NFO European CE/PE options with strike price.
4. get_nifty_atm_strike() calculates correct 50-point rounded ATM strike.
5. generate_nifty_option_chain_metadata() generates structured ladder with ITM/ATM/OTM flags.
6. All 6 supported historical timeframes: 1m, 5m, 15m, 30m, 1h, 1d.
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from core.enums import (
    AssetClass,
    Exchange,
    InstrumentType,
    OptionStyle,
    OptionType,
    Timeframe,
)
from data.nifty import (
    NIFTY_SUPPORTED_TIMEFRAMES,
    NIFTY_SYMBOL,
    create_nifty_future,
    create_nifty_index,
    create_nifty_option,
    generate_nifty_option_chain_metadata,
    get_nifty_atm_strike,
)


class TestNiftyData:

    def test_nifty_index_creation(self):
        index = create_nifty_index()
        assert index.symbol == NIFTY_SYMBOL
        assert index.exchange == Exchange.NSE
        assert index.asset_class == AssetClass.EQUITY
        assert index.instrument_type == InstrumentType.INDEX
        assert index.currency == "INR"

    def test_nifty_future_creation(self):
        expiry = datetime(2025, 2, 27, 10, 0, tzinfo=timezone.utc)
        fut = create_nifty_future(expiry=expiry, lot_size=75)

        assert fut.symbol == NIFTY_SYMBOL
        assert fut.exchange == Exchange.NFO
        assert fut.asset_class == AssetClass.FUTURES
        assert fut.instrument_type == InstrumentType.INDEX_FUTURES
        assert fut.expiry == expiry
        assert fut.lot_size == 75

    def test_nifty_option_creation(self):
        expiry = datetime(2025, 2, 27, 10, 0, tzinfo=timezone.utc)
        ce = create_nifty_option(
            strike=Decimal("24000"),
            option_type=OptionType.CALL,
            expiry=expiry,
            lot_size=75,
        )

        assert ce.symbol == NIFTY_SYMBOL
        assert ce.exchange == Exchange.NFO
        assert ce.asset_class == AssetClass.OPTIONS
        assert ce.instrument_type == InstrumentType.INDEX_OPTIONS
        assert ce.strike_price == Decimal("24000")
        assert ce.option_type == OptionType.CALL
        assert ce.option_style == OptionStyle.EUROPEAN
        assert ce.lot_size == 75

    def test_atm_strike_calculation(self):
        # Exact strike
        assert get_nifty_atm_strike(24000) == Decimal("24000")
        # Rounds down if below 25
        assert get_nifty_atm_strike(24020) == Decimal("24000")
        # Rounds up if >= 25
        assert get_nifty_atm_strike(24025) == Decimal("24050")
        assert get_nifty_atm_strike(24035) == Decimal("24050")
        assert get_nifty_atm_strike(24049.95) == Decimal("24050")

    def test_option_chain_metadata_generation(self):
        expiry = datetime(2025, 2, 27, 10, 0, tzinfo=timezone.utc)
        chain = generate_nifty_option_chain_metadata(
            spot_price=Decimal("24020"),
            expiry=expiry,
            num_strikes_each_side=5,
        )

        assert chain.underlying_symbol == NIFTY_SYMBOL
        assert chain.spot_price == Decimal("24020")
        assert chain.atm_strike == Decimal("24000")
        # 11 strikes * 2 types (CE and PE) = 22 contracts
        assert chain.total_contracts == 22
        assert len(chain.call_contracts) == 11
        assert len(chain.put_contracts) == 11

        # Check ATM classification
        atm_calls = [c for c in chain.call_contracts if c.is_atm]
        assert len(atm_calls) == 1
        assert atm_calls[0].strike_price == Decimal("24000")

    def test_supported_timeframes(self):
        expected = (
            Timeframe.M1,
            Timeframe.M5,
            Timeframe.M15,
            Timeframe.M30,
            Timeframe.H1,
            Timeframe.D1,
        )
        assert NIFTY_SUPPORTED_TIMEFRAMES == expected
