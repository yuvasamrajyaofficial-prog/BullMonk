"""
Unit tests for SessionCalendar and exchange session implementations.

Tests:
1. NSESessionCalendar trading days and holiday filtering.
2. NSESessionCalendar market hours (09:15-15:30 IST) and pre-open (09:00-09:15 IST).
3. NSESessionCalendar expected bar timestamps (e.g. 75 bars for 5m, 375 for 1m).
4. Crypto247SessionCalendar continuous 24/7 trading.
5. ForexSessionCalendar open hours (Sunday 21:00 UTC to Friday 21:00 UTC).
6. get_session_calendar factory resolution.
"""

from __future__ import annotations

from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

import pytest

from core.enums import Exchange, Timeframe
from data.sessions import (
    Crypto247SessionCalendar,
    ForexSessionCalendar,
    NSESessionCalendar,
    USSessionCalendar,
    get_session_calendar,
)


class TestSessionCalendars:

    def test_nse_trading_days(self):
        cal = NSESessionCalendar()
        # Monday 2025-01-06 is a trading day
        assert cal.is_trading_day(date(2025, 1, 6)) is True
        # Saturday 2025-01-11 is not a trading day
        assert cal.is_trading_day(date(2025, 1, 11)) is False
        # Sunday 2025-01-12 is not a trading day
        assert cal.is_trading_day(date(2025, 1, 12)) is False
        # Republic Day 2025-01-26 is a holiday
        assert cal.is_trading_day(date(2025, 1, 26)) is False

    def test_nse_market_hours_ist(self):
        cal = NSESessionCalendar()
        tz = ZoneInfo("Asia/Kolkata")

        # 09:15 IST is open
        t1 = datetime(2025, 1, 6, 9, 15, tzinfo=tz)
        assert cal.is_market_open(t1) is True

        # 12:00 IST is open
        t2 = datetime(2025, 1, 6, 12, 0, tzinfo=tz)
        assert cal.is_market_open(t2) is True

        # 15:29 IST is open
        t3 = datetime(2025, 1, 6, 15, 29, tzinfo=tz)
        assert cal.is_market_open(t3) is True

        # 15:30 IST is closed (end of session)
        t4 = datetime(2025, 1, 6, 15, 30, tzinfo=tz)
        assert cal.is_market_open(t4) is False

        # 09:10 IST is closed for regular trading (pre-open window)
        t5 = datetime(2025, 1, 6, 9, 10, tzinfo=tz)
        assert cal.is_market_open(t5) is False

    def test_nse_pre_open_session_window(self):
        cal = NSESessionCalendar()
        tz = ZoneInfo("Asia/Kolkata")
        t_pre = datetime(2025, 1, 6, 9, 5, tzinfo=tz)
        window = cal.get_session_window(t_pre)

        assert window is not None
        assert window.name == "pre_open"
        assert window.is_trading_active is False

    def test_nse_expected_bar_timestamps(self):
        cal = NSESessionCalendar()
        tz = ZoneInfo("Asia/Kolkata")
        # Full day 2025-01-06
        start = datetime(2025, 1, 6, 9, 15, tzinfo=tz)
        end = datetime(2025, 1, 6, 15, 30, tzinfo=tz)

        # 5-minute bars: 75 bars expected
        bars_5m = cal.expected_bar_timestamps(start, end, Timeframe.M5)
        assert len(bars_5m) == 75

        # 1-minute bars: 375 bars expected
        bars_1m = cal.expected_bar_timestamps(start, end, Timeframe.M1)
        assert len(bars_1m) == 375

    def test_crypto_247_continuous(self):
        cal = Crypto247SessionCalendar()
        sunday_midnight = datetime(2025, 1, 5, 0, 0, tzinfo=timezone.utc)
        assert cal.is_trading_day(sunday_midnight.date()) is True
        assert cal.is_market_open(sunday_midnight) is True

    def test_forex_sessions(self):
        cal = ForexSessionCalendar()
        # Saturday is closed
        saturday = datetime(2025, 1, 11, 12, 0, tzinfo=timezone.utc)
        assert cal.is_market_open(saturday) is False

        # Tuesday midday is open
        tuesday = datetime(2025, 1, 7, 12, 0, tzinfo=timezone.utc)
        assert cal.is_market_open(tuesday) is True

    def test_get_session_calendar_factory(self):
        assert isinstance(get_session_calendar(Exchange.NSE), NSESessionCalendar)
        assert isinstance(get_session_calendar(Exchange.NFO), NSESessionCalendar)
        assert isinstance(get_session_calendar(Exchange.BINANCE), Crypto247SessionCalendar)
        assert isinstance(get_session_calendar(Exchange.FOREX_OTC), ForexSessionCalendar)
        assert isinstance(get_session_calendar(Exchange.NYSE), USSessionCalendar)
