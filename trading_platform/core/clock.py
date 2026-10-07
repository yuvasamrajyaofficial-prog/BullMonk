"""
Platform clock abstraction.

The clock is injected throughout the system so that:
- Live trading uses the real wall-clock time.
- Backtesting uses a simulated clock that advances bar-by-bar.

This ensures deterministic, reproducible backtests without
modifying any strategy or engine code.

Timezone policy:
- Internally, all times are UTC.
- Exchange-local conversion happens at the market boundary layer only.
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from typing import Optional
import zoneinfo


class Clock(ABC):
    """Abstract base class for the platform clock."""

    @abstractmethod
    def now(self) -> datetime:
        """Return the current time as a timezone-aware UTC datetime."""

    @abstractmethod
    def now_local(self, tz: str) -> datetime:
        """
        Return the current time in the specified IANA timezone.

        Args:
            tz: IANA timezone string, e.g. 'Asia/Kolkata', 'UTC', 'America/New_York'.

        Returns:
            A timezone-aware datetime in the requested timezone.
        """

    @property
    @abstractmethod
    def is_simulated(self) -> bool:
        """Return True if this is a simulated (backtest) clock."""


class LiveClock(Clock):
    """
    Production wall-clock implementation.

    Uses system time. All times are UTC-normalised.
    """

    def now(self) -> datetime:
        """Return the current UTC time."""
        return datetime.now(tz=timezone.utc)

    def now_local(self, tz: str) -> datetime:
        """Return the current time in the given IANA timezone."""
        try:
            zone = zoneinfo.ZoneInfo(tz)
        except zoneinfo.ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: '{tz}'") from exc
        return datetime.now(tz=zone)

    @property
    def is_simulated(self) -> bool:
        return False

    def __repr__(self) -> str:
        return f"LiveClock(now={self.now().isoformat()})"


class SimulatedClock(Clock):
    """
    Deterministic simulated clock for backtesting.

    The clock starts at a given UTC datetime and can be advanced
    step-by-step by the backtest engine. Strategies and data providers
    interact with this clock transparently — no special-casing required.
    """

    def __init__(self, start_time: datetime) -> None:
        """
        Args:
            start_time: The initial UTC time for the simulation.
                        Must be timezone-aware.

        Raises:
            ValueError: If start_time is not timezone-aware.
        """
        if start_time.tzinfo is None:
            raise ValueError("SimulatedClock start_time must be timezone-aware.")
        self._current_time: datetime = start_time.astimezone(timezone.utc)

    def now(self) -> datetime:
        """Return the current simulated UTC time."""
        return self._current_time

    def now_local(self, tz: str) -> datetime:
        """Return the current simulated time in the given IANA timezone."""
        try:
            zone = zoneinfo.ZoneInfo(tz)
        except zoneinfo.ZoneInfoNotFoundError as exc:
            raise ValueError(f"Unknown timezone: '{tz}'") from exc
        return self._current_time.astimezone(zone)

    def advance(self, delta: timedelta) -> None:
        """
        Advance the simulated clock by a given timedelta.

        Args:
            delta: A positive timedelta. Negative deltas are rejected
                   to prevent temporal paradoxes in backtests.

        Raises:
            ValueError: If delta is not positive.
        """
        if delta.total_seconds() <= 0:
            raise ValueError("SimulatedClock.advance() requires a positive timedelta.")
        self._current_time += delta

    def set_time(self, new_time: datetime) -> None:
        """
        Directly set the simulated clock to a specific UTC time.

        Args:
            new_time: Target datetime (must be timezone-aware and >= current time).

        Raises:
            ValueError: If new_time is naive or is before the current time.
        """
        if new_time.tzinfo is None:
            raise ValueError("new_time must be timezone-aware.")
        new_utc = new_time.astimezone(timezone.utc)
        if new_utc < self._current_time:
            raise ValueError(
                f"SimulatedClock.set_time() cannot go backwards: "
                f"current={self._current_time.isoformat()}, "
                f"requested={new_utc.isoformat()}"
            )
        self._current_time = new_utc

    @property
    def is_simulated(self) -> bool:
        return True

    def __repr__(self) -> str:
        return f"SimulatedClock(current={self._current_time.isoformat()})"
