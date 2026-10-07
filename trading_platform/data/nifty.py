"""
NIFTY 50 concrete domain models, specifications, and option chain metadata.

Covers:
- NIFTY 50 Index (NSE cash index)
- NIFTY Index Futures (NFO futures contracts)
- NIFTY Index Options (NFO European options CE/PE)
- NIFTY Option Chain metadata & strike ladder generation
- Standard supported timeframes: 1m, 5m, 15m, 30m, 1h, 1d
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from core.enums import (
    AssetClass,
    DataSource,
    Exchange,
    InstrumentType,
    OptionStyle,
    OptionType,
    Timeframe,
)
from core.models import Asset

# Standard NIFTY constants
NIFTY_SYMBOL = "NIFTY"
NIFTY_LOT_SIZE = 75
NIFTY_STRIKE_INTERVAL = Decimal("50")
NIFTY_TICK_SIZE = Decimal("0.05")

# Officially supported historical bar resolutions
NIFTY_SUPPORTED_TIMEFRAMES: tuple[Timeframe, ...] = (
    Timeframe.M1,
    Timeframe.M5,
    Timeframe.M15,
    Timeframe.M30,
    Timeframe.H1,
    Timeframe.D1,
)


def create_nifty_index() -> Asset:
    """Create canonical Asset representation for NIFTY 50 Cash Index."""
    return Asset(
        symbol=NIFTY_SYMBOL,
        exchange=Exchange.NSE,
        asset_class=AssetClass.EQUITY,
        instrument_type=InstrumentType.INDEX,
        currency="INR",
        lot_size=1,
        tick_size=NIFTY_TICK_SIZE,
    )


def create_nifty_future(
    expiry: datetime,
    lot_size: int = NIFTY_LOT_SIZE,
) -> Asset:
    """
    Create Asset representation for a NIFTY Index Futures contract.

    Args:
        expiry: UTC timezone-aware contract expiry date/time.
        lot_size: Contract lot size (default 75).
    """
    if expiry.tzinfo is None:
        raise ValueError("expiry must be timezone-aware (UTC)")

    return Asset(
        symbol=NIFTY_SYMBOL,
        exchange=Exchange.NFO,
        asset_class=AssetClass.FUTURES,
        instrument_type=InstrumentType.INDEX_FUTURES,
        currency="INR",
        expiry=expiry,
        lot_size=lot_size,
        tick_size=NIFTY_TICK_SIZE,
    )


def create_nifty_option(
    strike: Decimal | int | float,
    option_type: OptionType,
    expiry: datetime,
    lot_size: int = NIFTY_LOT_SIZE,
) -> Asset:
    """
    Create Asset representation for a NIFTY Index European Option contract.

    Args:
        strike: Strike price (e.g. 24000, 24500).
        option_type: OptionType.CALL (CE) or OptionType.PUT (PE).
        expiry: UTC timezone-aware contract expiry.
        lot_size: Contract lot size (default 75).
    """
    if expiry.tzinfo is None:
        raise ValueError("expiry must be timezone-aware (UTC)")

    strike_dec = Decimal(str(strike))
    return Asset(
        symbol=NIFTY_SYMBOL,
        exchange=Exchange.NFO,
        asset_class=AssetClass.OPTIONS,
        instrument_type=InstrumentType.INDEX_OPTIONS,
        currency="INR",
        strike_price=strike_dec,
        option_type=option_type,
        option_style=OptionStyle.EUROPEAN,
        expiry=expiry,
        lot_size=lot_size,
        tick_size=NIFTY_TICK_SIZE,
    )


def get_nifty_atm_strike(spot_price: Decimal | float | int) -> Decimal:
    """
    Compute the At-The-Money (ATM) strike for NIFTY given current spot price.
    NIFTY strikes are spaced in 50-point increments.
    """
    spot = Decimal(str(spot_price))
    remainder = spot % NIFTY_STRIKE_INTERVAL
    if remainder >= (NIFTY_STRIKE_INTERVAL / 2):
        return spot + (NIFTY_STRIKE_INTERVAL - remainder)
    else:
        return spot - remainder


class NiftyOptionContractMetadata(BaseModel):
    """Metadata for an individual NIFTY option strike contract."""

    model_config = {"frozen": True}

    asset: Asset
    strike_price: Decimal
    option_type: OptionType
    expiry: datetime
    is_atm: bool = False
    is_itm: bool = False
    is_otm: bool = False

    @field_validator("strike_price")
    @classmethod
    def validate_strike(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("strike_price must be positive")
        return v


class NiftyOptionChainMetadata(BaseModel):
    """
    Snapshot metadata describing a NIFTY option chain structure.
    Does NOT require historical option tick data.
    """

    model_config = {"frozen": True}

    underlying_symbol: str = NIFTY_SYMBOL
    spot_price: Decimal
    atm_strike: Decimal
    expiry: datetime
    timestamp: datetime
    contracts: list[NiftyOptionContractMetadata] = Field(default_factory=list)

    @property
    def total_contracts(self) -> int:
        return len(self.contracts)

    @property
    def call_contracts(self) -> list[NiftyOptionContractMetadata]:
        return [c for c in self.contracts if c.option_type == OptionType.CALL]

    @property
    def put_contracts(self) -> list[NiftyOptionContractMetadata]:
        return [c for c in self.contracts if c.option_type == OptionType.PUT]


def generate_nifty_option_chain_metadata(
    spot_price: Decimal | float | int,
    expiry: datetime,
    timestamp: Optional[datetime] = None,
    num_strikes_each_side: int = 10,
    lot_size: int = NIFTY_LOT_SIZE,
) -> NiftyOptionChainMetadata:
    """
    Generate synthetic/structural option chain metadata for NIFTY.

    Constructs a symmetric strike ladder around the current spot price
    with correct ITM/ATM/OTM classification.
    """
    spot = Decimal(str(spot_price))
    atm = get_nifty_atm_strike(spot)
    ts = timestamp or datetime.now(tz=timezone.utc)
    if expiry.tzinfo is None:
        raise ValueError("expiry must be timezone-aware (UTC)")
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware (UTC)")

    contracts: list[NiftyOptionContractMetadata] = []

    # Strike ladder
    strikes = [
        atm + (i * NIFTY_STRIKE_INTERVAL)
        for i in range(-num_strikes_each_side, num_strikes_each_side + 1)
    ]

    for strike in strikes:
        is_atm = (strike == atm)
        for opt_type in (OptionType.CALL, OptionType.PUT):
            asset = create_nifty_option(
                strike=strike,
                option_type=opt_type,
                expiry=expiry,
                lot_size=lot_size,
            )

            if opt_type == OptionType.CALL:
                is_itm = (strike < spot) and not is_atm
                is_otm = (strike > spot) and not is_atm
            else:
                is_itm = (strike > spot) and not is_atm
                is_otm = (strike < spot) and not is_atm

            contracts.append(
                NiftyOptionContractMetadata(
                    asset=asset,
                    strike_price=strike,
                    option_type=opt_type,
                    expiry=expiry,
                    is_atm=is_atm,
                    is_itm=is_itm,
                    is_otm=is_otm,
                )
            )

    return NiftyOptionChainMetadata(
        underlying_symbol=NIFTY_SYMBOL,
        spot_price=spot,
        atm_strike=atm,
        expiry=expiry,
        timestamp=ts,
        contracts=contracts,
    )
