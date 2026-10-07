# BullMonk Trading Platform

> **Phase 1 — Engineering Foundation**
> This phase establishes the architecture. No live trading capability is present yet.

---

## Overview

BullMonk is a production-grade, modular algorithmic trading platform designed for:

| Asset Class | Instruments |
|---|---|
| Indian Equities | Stocks on NSE / BSE |
| Indian Derivatives | NIFTY / BankNIFTY futures and options (NFO) |
| Forex | Major and minor currency pairs |
| Cryptocurrency | BTC, ETH, and altcoin spot / futures |

**Planned capabilities** (future phases):
- Historical backtesting with deterministic replay
- Walk-forward testing and Monte Carlo analysis
- Paper trading and live broker integration
- Multi-user SaaS with subscription billing
- Strategy marketplace

---

## Architecture

The platform is built on a strict **layered, event-driven architecture**:

```
┌────────────────────────────────────────────────────────────┐
│                        Strategies                          │
│  (Pure logic. No broker knowledge. Emit Signals only.)     │
└──────────────────────────┬─────────────────────────────────┘
                           │ Signal events
┌──────────────────────────▼─────────────────────────────────┐
│                       Risk Manager                         │
│  (Validates every order before execution. Gatekeeper.)     │
└──────────────────────────┬─────────────────────────────────┘
                           │ Approved orders
┌──────────────────────────▼─────────────────────────────────┐
│                      Order Executor                        │
│  (Translates signals → orders → broker calls.)             │
└──────────────────────────┬─────────────────────────────────┘
                           │ Generic broker interface
┌──────────────────────────▼─────────────────────────────────┐
│                   Broker Adapters (future)                  │
│  Dhan │ Zerodha │ Upstox │ Fyers │ Binance │ …            │
└────────────────────────────────────────────────────────────┘
```

**Core design principles:**
- Strategies never import broker code.
- Brokers never import strategy code.
- All communication flows through typed domain events on the `EventBus`.
- `SimulatedClock` (backtesting) and `LiveClock` are interchangeable — no special-casing.
- All timestamps are UTC internally; local conversion happens at the market boundary.

---

## Directory Structure

```
trading_platform/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example          ← Copy to .env, fill secrets
├── requirements.txt
├── pyproject.toml
│
├── config/
│   └── settings.py       ← Typed config via pydantic-settings
│
├── core/
│   ├── enums.py          ← All domain enumerations
│   ├── models.py         ← All domain models (Pydantic v2)
│   ├── exceptions.py     ← Domain exception hierarchy
│   ├── events.py         ← EventBus + typed event classes
│   └── clock.py          ← LiveClock + SimulatedClock
│
├── data/
│   ├── interfaces.py     ← HistoricalDataProvider, LiveMarketDataProvider
│   └── models.py         ← DataQualityReport, SubscriptionConfig
│
├── strategies/
│   ├── base.py           ← BaseStrategy abstract class
│   └── models.py         ← StrategyPerformanceSummary
│
├── execution/
│   ├── interfaces.py     ← OrderExecutor, PortfolioRepository
│   └── models.py         ← ExecutionReport, CommissionSchedule
│
├── brokers/
│   └── base.py           ← BaseBroker abstract interface
│
├── risk/
│   └── manager.py        ← RiskManager with 5 gating checks
│
├── portfolio/
│   └── portfolio.py      ← In-memory Portfolio manager
│
├── backtesting/
│   └── engine.py         ← BacktestEngine interface + SimpleBacktestEngine
│
├── analytics/
│   └── metrics.py        ← AnalyticsEngine (win rate, drawdown, PF, etc.)
│
├── tests/
│   ├── unit/             ← Unit tests per module
│   └── integration/      ← Cross-module smoke tests
│
├── scripts/
│   └── health_check.py   ← Environment verification script
│
└── logging_config.py     ← Centralised logging with 5 named channels
```

---

## Installation

```bash
# 1. Clone the repository
git clone <repo-url>
cd trading_platform

# 2. Create a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / macOS
# Edit .env with your credentials
```

---

## Configuration

All settings come from environment variables (or a `.env` file).
**Never commit `.env` to source control.**

| Variable | Required | Description |
|---|---|---|
| `ENVIRONMENT` | No | `development` / `staging` / `production` |
| `LOG_LEVEL` | No | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `DATABASE_URL` | Production | PostgreSQL connection string |
| `REDIS_URL` | Production | Redis connection string |
| `JWT_SECRET` | Production | JWT signing secret |
| `DHAN_CLIENT_ID` | Dhan users | Dhan client ID |
| `DHAN_ACCESS_TOKEN` | Dhan users | Dhan API token |
| `ZERODHA_API_KEY` | Future | Zerodha API key |
| `BINANCE_API_KEY` | Future | Binance API key |

See `.env.example` for the full list.

---

## Running Tests

```bash
cd trading_platform

# Run the full test suite
python -m pytest

# Run with coverage report
python -m pytest --cov=. --cov-report=term-missing

# Run a specific test file
python -m pytest tests/unit/test_models.py -v
```

---

## Health Check

```bash
cd trading_platform
python scripts/health_check.py
```

Expected output on a healthy environment:
```
✓ Python 3.14.x
✓ Pydantic v2 importable
✓ All platform modules import cleanly
✓ Settings instantiation
✓ No hard-coded secrets
✓ Asset models (equity, options, crypto, forex)
✓ LiveClock returns UTC
✓ SimulatedClock advance
✓ EventBus publish/subscribe
✓ Logging configuration

✓ All checks passed. Environment: READY for development.
```

---

## Development Roadmap

| Phase | Status | Description |
|---|---|---|
| Phase 1 | ✅ Complete | Engineering foundation & architecture |
| Phase 2 | ⏳ Planned | Backtest engine with order simulation |
| Phase 3 | ⏳ Planned | Dhan broker adapter (live + paper trading) |
| Phase 4 | ⏳ Planned | Walk-forward testing + Monte Carlo |
| Phase 5 | ⏳ Planned | Zerodha / Upstox / Binance adapters |
| Phase 6 | ⏳ Planned | SaaS multi-user, billing, user accounts |
| Phase 7 | ⏳ Planned | Strategy marketplace |

---

## Security Principles

1. **No hard-coded credentials** — All secrets via environment variables.
2. **Never log secrets** — The `SanitizingFilter` redacts credential patterns.
3. **Broker isolation** — Strategy code can never import broker adapters.
4. **Fail-fast config** — Missing required production variables raise errors on startup.
5. **Timezone safety** — All times are UTC internally; naive datetimes are rejected.
6. **Immutable models** — Market data models are frozen (Pydantic `frozen=True`).
7. **No fabricated data** — The system never generates synthetic market prices.

---

## Contributing

This codebase follows:
- PEP 8 style
- Strong type hints throughout
- Pydantic v2 for all domain models
- SOLID principles where applicable
- Dependency injection for clocks, event buses, and data providers

Run `python -m compileall .` before submitting any PR.

---

*BullMonk Trading Platform — Phase 1 Engineering Foundation*
*Not intended for live trading in its current state.*
