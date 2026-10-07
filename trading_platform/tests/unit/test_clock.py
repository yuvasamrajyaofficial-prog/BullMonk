"""
Unit tests for the clock abstraction.

Tests that:
1. LiveClock returns UTC timezone-aware datetime.
2. SimulatedClock starts at the correct time.
3. SimulatedClock advances correctly.
4. SimulatedClock rejects backwards time travel.
5. SimulatedClock rejects naive timestamps.
6. Local timezone conversion works.
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta

from core.clock import LiveClock, SimulatedClock


class TestLiveClock:
    def test_returns_utc(self):
        clock = LiveClock()
        now = clock.now()
        assert now.tzinfo is not None
        assert now.tzinfo == timezone.utc or str(now.tzinfo) == "UTC"

    def test_is_not_simulated(self):
        assert not LiveClock().is_simulated

    def test_now_local_kolkata(self):
        clock = LiveClock()
        local = clock.now_local("Asia/Kolkata")
        assert local.tzinfo is not None
        assert "Asia/Kolkata" in str(local.tzinfo) or "IST" in str(local.tzinfo)

    def test_invalid_timezone_raises(self):
        clock = LiveClock()
        with pytest.raises(ValueError, match="Unknown timezone"):
            clock.now_local("Invalid/Timezone")


class TestSimulatedClock:
    @pytest.fixture
    def start_time(self) -> datetime:
        return datetime(2024, 1, 15, 9, 15, 0, tzinfo=timezone.utc)

    @pytest.fixture
    def sim_clock(self, start_time: datetime) -> SimulatedClock:
        return SimulatedClock(start_time=start_time)

    def test_starts_at_correct_time(self, sim_clock: SimulatedClock, start_time: datetime):
        assert sim_clock.now() == start_time

    def test_is_simulated(self, sim_clock: SimulatedClock):
        assert sim_clock.is_simulated

    def test_advance_by_one_minute(self, sim_clock: SimulatedClock, start_time: datetime):
        sim_clock.advance(timedelta(minutes=1))
        expected = start_time + timedelta(minutes=1)
        assert sim_clock.now() == expected

    def test_advance_multiple_times(self, sim_clock: SimulatedClock, start_time: datetime):
        sim_clock.advance(timedelta(minutes=5))
        sim_clock.advance(timedelta(hours=1))
        expected = start_time + timedelta(minutes=5) + timedelta(hours=1)
        assert sim_clock.now() == expected

    def test_advance_zero_raises(self, sim_clock: SimulatedClock):
        with pytest.raises(ValueError):
            sim_clock.advance(timedelta(seconds=0))

    def test_advance_negative_raises(self, sim_clock: SimulatedClock):
        with pytest.raises(ValueError):
            sim_clock.advance(timedelta(seconds=-1))

    def test_set_time_valid(self, sim_clock: SimulatedClock, start_time: datetime):
        new_time = start_time + timedelta(hours=2)
        sim_clock.set_time(new_time)
        assert sim_clock.now() == new_time

    def test_set_time_backwards_raises(self, sim_clock: SimulatedClock, start_time: datetime):
        with pytest.raises(ValueError, match="backwards"):
            sim_clock.set_time(start_time - timedelta(seconds=1))

    def test_set_time_naive_raises(self, sim_clock: SimulatedClock):
        with pytest.raises(ValueError):
            sim_clock.set_time(datetime(2024, 1, 16, 10, 0, 0))  # no tzinfo

    def test_naive_start_time_raises(self):
        with pytest.raises(ValueError):
            SimulatedClock(start_time=datetime(2024, 1, 1))  # naive

    def test_local_time_kolkata(self, sim_clock: SimulatedClock):
        # UTC 09:15 = IST 14:45
        local = sim_clock.now_local("Asia/Kolkata")
        assert local.hour == 14
        assert local.minute == 45
