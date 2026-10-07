"""
Market session calendars and trading hours abstraction.

Supports exchange-specific session schedules, weekend filtering,
holiday calendars, and expected bar timestamp generation.
Designed to support:
- NSE (Indian equities and derivatives)
- Crypto 24/7 continuous trading
- Forex (Sunday 21:00 UTC to Friday 21:00 UTC)
- US Equities (NYSE / NASDAQ)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from core.enums import Exchange, Timeframe


@dataclass(frozen=True)
class SessionWindow:
    """A distinct trading or auction window within a trading day."""

    name: str
    open_time: time
    close_time: time
    is_trading_active: bool = True

    def contains_time(self, t: time) -> bool:
        """Return True if time t is within [open_time, close_time)."""
        return self.open_time <= t < self.close_time


def _timeframe_to_timedelta(tf: Timeframe) -> timedelta:
    """Convert Timeframe enum to timedelta."""
    mapping = {
        Timeframe.S1: timedelta(seconds=1),
        Timeframe.M1: timedelta(minutes=1),
        Timeframe.M2: timedelta(minutes=2),
        Timeframe.M3: timedelta(minutes=3),
        Timeframe.M5: timedelta(minutes=5),
        Timeframe.M10: timedelta(minutes=10),
        Timeframe.M15: timedelta(minutes=15),
        Timeframe.M30: timedelta(minutes=30),
        Timeframe.H1: timedelta(hours=1),
        Timeframe.H2: timedelta(hours=2),
        Timeframe.H4: timedelta(hours=4),
        Timeframe.D1: timedelta(days=1),
        Timeframe.W1: timedelta(weeks=1),
        Timeframe.MN1: timedelta(days=30),
    }
    return mapping[tf]


class SessionCalendar(ABC):
    """
    Abstract calendar defining when a market is open for trading.
    """

    @property
    @abstractmethod
    def exchange(self) -> Exchange:
        """The primary exchange this calendar models."""

    @property
    @abstractmethod
    def timezone_name(self) -> str:
        """Local timezone name for the exchange (e.g. 'Asia/Kolkata')."""

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone_name)

    @abstractmethod
    def is_trading_day(self, d: date | datetime) -> bool:
        """Return True if the date is a scheduled trading day (not a weekend or holiday)."""

    @abstractmethod
    def is_market_open(self, dt: datetime) -> bool:
        """Return True if the exchange is actively trading at datetime dt (UTC or local)."""

    @abstractmethod
    def get_session_window(self, dt: datetime) -> Optional[SessionWindow]:
        """Return the active SessionWindow for dt, or None if market is closed."""

    @abstractmethod
    def get_trading_intervals(
        self, start_date: date, end_date: date
    ) -> list[tuple[datetime, datetime]]:
        """
        Return list of (session_open_utc, session_close_utc) intervals
        for all trading days between start_date and end_date (inclusive).
        """

    def expected_bar_timestamps(
        self, start: datetime, end: datetime, timeframe: Timeframe
    ) -> list[datetime]:
        """
        Generate all expected bar open timestamps (UTC) in range [start, end)
        according to the market session rules and granularity.
        """
        step = _timeframe_to_timedelta(timeframe)
        if start.tzinfo is None or end.tzinfo is None:
            raise ValueError("start and end must be timezone-aware")

        start_utc = start.astimezone(timezone.utc)
        end_utc = end.astimezone(timezone.utc)

        # For daily/weekly bars
        if timeframe in (Timeframe.D1, Timeframe.W1, Timeframe.MN1):
            curr_date = start_utc.date()
            end_date = end_utc.date()
            timestamps: list[datetime] = []
            while curr_date <= end_date:
                if self.is_trading_day(curr_date):
                    intervals = self.get_trading_intervals(curr_date, curr_date)
                    if intervals:
                        bar_ts = intervals[0][0]
                        if start_utc <= bar_ts <= end_utc:
                            timestamps.append(bar_ts)
                curr_date += timedelta(days=1)
            return timestamps

        # For intraday bars
        start_date = start_utc.astimezone(self.tz).date()
        end_date = end_utc.astimezone(self.tz).date()
        session_intervals = self.get_trading_intervals(start_date, end_date)

        timestamps = []
        for sess_open, sess_close in session_intervals:
            curr = sess_open
            while curr + step <= sess_close:
                if start_utc <= curr <= end_utc:
                    timestamps.append(curr)
                curr += step

        return sorted(timestamps)


class NSESessionCalendar(SessionCalendar):
    """
    Session calendar for the National Stock Exchange of India (NSE/NFO).

    - Regular trading hours: 09:15 to 15:30 IST (03:45 to 10:00 UTC)
    - Pre-open session: 09:00 to 09:15 IST (03:30 to 03:45 UTC)
    - Trading days: Monday through Friday (excluding configured holidays)
    - Timezone: Asia/Kolkata (UTC+05:30)
    """

    REGULAR_OPEN = time(9, 15)
    REGULAR_CLOSE = time(15, 30)
    PRE_OPEN_START = time(9, 0)
    PRE_OPEN_END = time(9, 15)

    def __init__(self, holidays: Optional[set[date]] = None) -> None:
        self._exchange = Exchange.NSE
        self._holidays: set[date] = holidays or self._default_nse_holidays()
        self._regular_window = SessionWindow(
            name="regular",
            open_time=self.REGULAR_OPEN,
            close_time=self.REGULAR_CLOSE,
            is_trading_active=True,
        )
        self._pre_open_window = SessionWindow(
            name="pre_open",
            open_time=self.PRE_OPEN_START,
            close_time=self.PRE_OPEN_END,
            is_trading_active=False,
        )

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def timezone_name(self) -> str:
        return "Asia/Kolkata"

    @staticmethod
    def _default_nse_holidays() -> set[date]:
        """A baseline set of national Indian market holidays for test/reference."""
        return {
            date(2025, 1, 26),   # Republic Day
            date(2025, 3, 14),   # Holi
            date(2025, 3, 31),   # Id-Ul-Fitr
            date(2025, 4, 10),   # Mahavir Jayanti
            date(2025, 4, 14),   # Dr. Ambedkar Jayanti
            date(2025, 4, 18),   # Good Friday
            date(2025, 5, 1),    # Maharashtra Day
            date(2025, 8, 15),   # Independence Day
            date(2025, 8, 27),   # Ganesh Chaturthi
            date(2025, 10, 2),   # Mahatma Gandhi Jayanti
            date(2025, 10, 21),  # Diwali Laxmi Pujan
            date(2025, 10, 22),  # Diwali Balipratipada
            date(2025, 11, 5),   # Guru Nanak Jayanti
            date(2025, 12, 25),  # Christmas
            # 2024 reference holidays
            date(2024, 1, 26),
            date(2024, 3, 8),
            date(2024, 3, 25),
            date(2024, 3, 29),
            date(2024, 4, 11),
            date(2024, 4, 17),
            date(2024, 5, 1),
            date(2024, 6, 17),
            date(2024, 7, 17),
            date(2024, 8, 15),
            date(2024, 10, 2),
            date(2024, 11, 1),
            date(2024, 11, 15),
            date(2024, 12, 25),
        }

    def is_trading_day(self, d: date | datetime) -> bool:
        target_date = d.date() if isinstance(d, datetime) else d
        # Monday is 0, Sunday is 6
        if target_date.weekday() in (5, 6):
            return False
        if target_date in self._holidays:
            return False
        return True

    def is_market_open(self, dt: datetime) -> bool:
        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        local_dt = dt.astimezone(self.tz)
        if not self.is_trading_day(local_dt.date()):
            return False
        return self._regular_window.contains_time(local_dt.time())

    def get_session_window(self, dt: datetime) -> Optional[SessionWindow]:
        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        local_dt = dt.astimezone(self.tz)
        if not self.is_trading_day(local_dt.date()):
            return None
        t = local_dt.time()
        if self._regular_window.contains_time(t):
            return self._regular_window
        if self._pre_open_window.contains_time(t):
            return self._pre_open_window
        return None

    def get_trading_intervals(
        self, start_date: date, end_date: date
    ) -> list[tuple[datetime, datetime]]:
        intervals: list[tuple[datetime, datetime]] = []
        curr = start_date
        while curr <= end_date:
            if self.is_trading_day(curr):
                open_local = datetime.combine(curr, self.REGULAR_OPEN, tzinfo=self.tz)
                close_local = datetime.combine(curr, self.REGULAR_CLOSE, tzinfo=self.tz)
                intervals.append((
                    open_local.astimezone(timezone.utc),
                    close_local.astimezone(timezone.utc),
                ))
            curr += timedelta(days=1)
        return intervals


class Crypto247SessionCalendar(SessionCalendar):
    """
    Session calendar for 24/7 continuous cryptocurrency markets (e.g. Binance).
    Every second of every day is trading active.
    """

    def __init__(self, exchange: Exchange = Exchange.BINANCE) -> None:
        self._exchange = exchange
        self._window = SessionWindow(
            name="continuous_247",
            open_time=time(0, 0),
            close_time=time(23, 59, 59),
            is_trading_active=True,
        )

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def timezone_name(self) -> str:
        return "UTC"

    def is_trading_day(self, d: date | datetime) -> bool:
        return True

    def is_market_open(self, dt: datetime) -> bool:
        return True

    def get_session_window(self, dt: datetime) -> Optional[SessionWindow]:
        return self._window

    def get_trading_intervals(
        self, start_date: date, end_date: date
    ) -> list[tuple[datetime, datetime]]:
        intervals: list[tuple[datetime, datetime]] = []
        curr = start_date
        while curr <= end_date:
            start_utc = datetime.combine(curr, time(0, 0), tzinfo=timezone.utc)
            end_utc = datetime.combine(curr + timedelta(days=1), time(0, 0), tzinfo=timezone.utc)
            intervals.append((start_utc, end_utc))
            curr += timedelta(days=1)
        return intervals


class ForexSessionCalendar(SessionCalendar):
    """
    Forex OTC market session calendar.
    Market opens Sunday 21:00 UTC (Sydney open) and closes Friday 21:00 UTC (NY close).
    """

    def __init__(self) -> None:
        self._exchange = Exchange.FOREX_OTC

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def timezone_name(self) -> str:
        return "UTC"

    def is_trading_day(self, d: date | datetime) -> bool:
        target_date = d.date() if isinstance(d, datetime) else d
        # Saturday is always closed
        return target_date.weekday() != 5

    def is_market_open(self, dt: datetime) -> bool:
        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        dt_utc = dt.astimezone(timezone.utc)
        wd = dt_utc.weekday()
        t = dt_utc.time()

        if wd == 5:  # Saturday
            return False
        if wd == 6:  # Sunday open after 21:00 UTC
            return t >= time(21, 0)
        if wd == 4:  # Friday close at 21:00 UTC
            return t < time(21, 0)
        return True  # Mon, Tue, Wed, Thu 24h open

    def get_session_window(self, dt: datetime) -> Optional[SessionWindow]:
        if self.is_market_open(dt):
            return SessionWindow("forex_active", time(0, 0), time(23, 59, 59), True)
        return None

    def get_trading_intervals(
        self, start_date: date, end_date: date
    ) -> list[tuple[datetime, datetime]]:
        intervals: list[tuple[datetime, datetime]] = []
        curr = start_date
        while curr <= end_date:
            wd = curr.weekday()
            if wd == 5:  # Saturday
                pass
            elif wd == 6:  # Sunday
                open_utc = datetime.combine(curr, time(21, 0), tzinfo=timezone.utc)
                close_utc = datetime.combine(curr + timedelta(days=1), time(0, 0), tzinfo=timezone.utc)
                intervals.append((open_utc, close_utc))
            elif wd == 4:  # Friday
                open_utc = datetime.combine(curr, time(0, 0), tzinfo=timezone.utc)
                close_utc = datetime.combine(curr, time(21, 0), tzinfo=timezone.utc)
                intervals.append((open_utc, close_utc))
            else:  # Mon, Tue, Wed, Thu
                open_utc = datetime.combine(curr, time(0, 0), tzinfo=timezone.utc)
                close_utc = datetime.combine(curr + timedelta(days=1), time(0, 0), tzinfo=timezone.utc)
                intervals.append((open_utc, close_utc))
            curr += timedelta(days=1)
        return intervals


class USSessionCalendar(SessionCalendar):
    """US Regular Trading Hours (NYSE / NASDAQ): 09:30 to 16:00 ET."""

    def __init__(self, exchange: Exchange = Exchange.NYSE) -> None:
        self._exchange = exchange
        self._window = SessionWindow("us_regular", time(9, 30), time(16, 0), True)

    @property
    def exchange(self) -> Exchange:
        return self._exchange

    @property
    def timezone_name(self) -> str:
        return "America/New_York"

    def is_trading_day(self, d: date | datetime) -> bool:
        target_date = d.date() if isinstance(d, datetime) else d
        return target_date.weekday() not in (5, 6)

    def is_market_open(self, dt: datetime) -> bool:
        if dt.tzinfo is None:
            raise ValueError("datetime must be timezone-aware")
        local_dt = dt.astimezone(self.tz)
        if not self.is_trading_day(local_dt.date()):
            return False
        return self._window.contains_time(local_dt.time())

    def get_session_window(self, dt: datetime) -> Optional[SessionWindow]:
        if self.is_market_open(dt):
            return self._window
        return None

    def get_trading_intervals(
        self, start_date: date, end_date: date
    ) -> list[tuple[datetime, datetime]]:
        intervals: list[tuple[datetime, datetime]] = []
        curr = start_date
        while curr <= end_date:
            if self.is_trading_day(curr):
                open_local = datetime.combine(curr, time(9, 30), tzinfo=self.tz)
                close_local = datetime.combine(curr, time(16, 0), tzinfo=self.tz)
                intervals.append((
                    open_local.astimezone(timezone.utc),
                    close_local.astimezone(timezone.utc),
                ))
            curr += timedelta(days=1)
        return intervals


def get_session_calendar(exchange: Exchange | str) -> SessionCalendar:
    """Factory to retrieve the appropriate session calendar for an exchange."""
    val = exchange.value if isinstance(exchange, Exchange) else str(exchange).upper()
    if val in (Exchange.NSE.value, Exchange.BSE.value, Exchange.NFO.value, Exchange.BFO.value):
        return NSESessionCalendar()
    if val in (Exchange.BINANCE.value, Exchange.COINBASE.value, Exchange.BYBIT.value):
        return Crypto247SessionCalendar(Exchange(val))
    if val in (Exchange.FOREX_OTC.value, Exchange.CDS.value):
        return ForexSessionCalendar()
    if val in (Exchange.NYSE.value, Exchange.NASDAQ.value):
        return USSessionCalendar(Exchange(val))
    # Default fallback to NSE calendar
    return NSESessionCalendar()
