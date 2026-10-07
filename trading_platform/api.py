"""
FastAPI REST API Server for the BullMonk Quantitative Trading Engine.

Exposes endpoints for:
- Health & System Status
- Quantitative Indicator Registry inspection
- Multi-factor Feature Pipeline calculation
- Black-Scholes European Option Pricing & analytical Greeks
- Delta-Target Strike Selection
- Synthetic & Cached Market Data streaming
- Event-driven Strategy Backtesting

Usage:
    uvicorn trading_platform.api:app --host 0.0.0.0 --port 8000 --reload
    or
    python -m trading_platform.api
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

# Ensure trading_platform is in sys.path
_CURRENT_DIR = Path(__file__).resolve().parent
_PARENT_DIR = _CURRENT_DIR.parent
for _p in (str(_CURRENT_DIR), str(_PARENT_DIR)):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.enums import Timeframe
from data.nifty import create_nifty_index
from data.sessions import NSESessionCalendar, get_session_calendar
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
from indicators import (
    BlackScholesGreeks,
    DeltaTargetOptionSelector,
    FeaturePipeline,
    calculate_black_scholes,
    default_registry,
)

app = FastAPI(
    title="BullMonk Quantitative Trading Engine API",
    version="1.0.0",
    description="REST API interface for BullMonk indicators, options Greeks, backtesting, and market data.",
)

# Enable CORS for Cloudflare Pages, Vercel, and local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------------------------------------------------
# Request & Response Models
# -----------------------------------------------------------------------------

class GreeksRequest(BaseModel):
    spot: float = Field(..., gt=0, description="Underlying spot price")
    strike: float = Field(..., gt=0, description="Option strike price")
    time_to_expiry_years: float = Field(..., description="Time to expiry in years (e.g. 7/365)")
    volatility: float = Field(..., gt=0, description="Annualized volatility (e.g. 0.15 for 15%)")
    risk_free_rate: float = Field(default=0.065, description="Risk-free interest rate")
    option_type: str = Field(default="call", description="'call' or 'put'")


class StrikeSelectionRequest(BaseModel):
    spot: float = Field(..., gt=0)
    available_strikes: List[float] = Field(..., min_length=1)
    time_to_expiry_years: float = Field(...)
    volatility: float = Field(..., gt=0)
    target_delta: float = Field(..., description="Target delta (e.g. 0.50, 0.70)")
    option_type: str = Field(default="call")
    risk_free_rate: float = Field(default=0.065)


class IndicatorConfigRequest(BaseModel):
    name: str
    params: Dict[str, Any] = Field(default_factory=dict)


class FeatureCalculationRequest(BaseModel):
    indicators: List[IndicatorConfigRequest]
    bars: Optional[List[Dict[str, Any]]] = None  # If None, uses synthetic NIFTY data


# -----------------------------------------------------------------------------
# Endpoints
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    """Welcome and quick links."""
    return {
        "message": "BullMonk Quantitative Trading Engine API is running!",
        "interactive_docs": "/docs",
        "health": "/api/health",
        "indicators": "/api/indicators",
    }


@app.get("/api/health")
def health_check():
    """Health status and platform metadata."""
    return {
        "status": "online",
        "service": "BullMonk Quantitative Engine",
        "version": "1.0.0",
        "engine": "Python 3.13 / FastAPI",
        "indicators_count": len(default_registry.list_indicators()),
    }


@app.get("/api/indicators")
def list_indicators():
    """Return all 29 registered quantitative indicators and their metadata."""
    return default_registry.list_indicators()


@app.get("/api/market-data/synthetic")
def get_synthetic_market_data(
    sessions: int = Query(default=3, ge=1, le=10),
    timeframe: str = Query(default="5m"),
):
    """Generate deterministic synthetic NIFTY 50 OHLCV data."""
    tf_enum = Timeframe(timeframe.lower()) if timeframe.lower() in [t.value for t in Timeframe] else Timeframe.M5
    gen = SyntheticOHLCVGenerator(seed=42)
    cfg = SyntheticDataConfig(
        asset=create_nifty_index(),
        number_of_sessions=sessions,
        timeframe=tf_enum,
        start_price=Decimal("24000.00"),
        volatility=0.15,
        seed=42,
    )
    bars = gen.generate(cfg)
    return [
        {
            "timestamp": b.timestamp.isoformat(),
            "open": float(b.open),
            "high": float(b.high),
            "low": float(b.low),
            "close": float(b.close),
            "volume": float(b.volume),
        }
        for b in bars
    ]


@app.post("/api/options/greeks")
def get_options_greeks(req: GreeksRequest):
    """Calculate Black-Scholes European theoretical option price and analytical Greeks."""
    try:
        greeks = calculate_black_scholes(
            spot=req.spot,
            strike=req.strike,
            time_to_expiry=req.time_to_expiry_years,
            volatility=req.volatility,
            risk_free_rate=req.risk_free_rate,
            option_type=req.option_type,
        )
        return {
            "spot": req.spot,
            "strike": req.strike,
            "option_type": req.option_type,
            "price": round(greeks.price, 2),
            "delta": round(greeks.delta, 4),
            "gamma": round(greeks.gamma, 6),
            "theta_daily": round(greeks.theta_daily, 2),
            "theta_annual": round(greeks.theta_annual, 2),
            "vega_1pct": round(greeks.vega_1pct, 2),
            "vega_annual": round(greeks.vega_annual, 2),
            "disclaimer": "Historical/theoretical option pricing is not a substitute for live executable option quotes.",
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/options/select-strike")
def select_strike_target_delta(req: StrikeSelectionRequest):
    """Identify the option strike closest to the target delta."""
    try:
        result = DeltaTargetOptionSelector.select_strike(
            spot=req.spot,
            available_strikes=req.available_strikes,
            time_to_expiry_years=req.time_to_expiry_years,
            volatility=req.volatility,
            target_delta=req.target_delta,
            option_type=req.option_type,
            risk_free_rate=req.risk_free_rate,
        )
        return {
            "selected_strike": result.selected_strike,
            "target_delta": result.target_delta,
            "actual_delta": round(result.actual_delta, 4),
            "delta_error": round(result.delta_error, 4),
            "theoretical_price": round(result.theoretical_price, 2),
            "gamma": round(result.greeks.gamma, 6),
            "theta_daily": round(result.greeks.theta_daily, 2),
            "vega_1pct": round(result.greeks.vega_1pct, 2),
            "all_evaluated": result.all_evaluated,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/indicators/calculate")
def calculate_feature_pipeline(req: FeatureCalculationRequest):
    """Execute a FeaturePipeline on bars and return the feature matrix."""
    try:
        # Instantiate requested indicators
        indicators_to_run = []
        for ind_cfg in req.indicators:
            ind_instance = default_registry.get(ind_cfg.name, **ind_cfg.params)
            indicators_to_run.append(ind_instance)

        pipeline = FeaturePipeline(indicators_to_run)

        # Prepare DataFrame
        if req.bars:
            df = pd.DataFrame(req.bars)
            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
        else:
            # Default to synthetic bars
            gen = SyntheticOHLCVGenerator(seed=42)
            cfg = SyntheticDataConfig(number_of_sessions=2, timeframe=Timeframe.M5, seed=42)
            bars = gen.generate(cfg)
            df = pd.DataFrame([
                {
                    "timestamp": b.timestamp,
                    "open": float(b.open),
                    "high": float(b.high),
                    "low": float(b.low),
                    "close": float(b.close),
                    "volume": float(b.volume),
                }
                for b in bars
            ])

        features_df = pipeline.calculate(df)

        # Convert timestamps and NaNs safely for JSON
        res_data = features_df.replace({np.nan: None}).to_dict(orient="records")
        for row in res_data:
            if "timestamp" in row and hasattr(row["timestamp"], "isoformat"):
                row["timestamp"] = row["timestamp"].isoformat()

        return {
            "total_bars": len(features_df),
            "columns": list(features_df.columns),
            "max_warmup_period": pipeline.max_warmup_period,
            "latest_values": res_data[-1] if res_data else {},
            "sample_bars": res_data[-50:] if len(res_data) > 50 else res_data,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
