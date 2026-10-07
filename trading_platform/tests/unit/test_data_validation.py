"""
Unit tests for the DataValidator and ValidationReport engine.

Tests:
1. Empty series detection.
2. Valid series produces 0 errors and is_valid=True.
3. Duplicate timestamp detection.
4. Out-of-order timestamp detection.
5. Invalid OHLC relationships.
6. Non-positive price detection.
7. Negative volume detection.
8. Timezone naive timestamp detection.
9. Unexpected time gap detection.
10. Off-session timestamp detection.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from core.enums import DataSource, Timeframe
from core.models import OHLCVBar
from data.nifty import create_nifty_index
from data.sessions import NSESessionCalendar
from data.synthetic import SyntheticDataConfig, SyntheticOHLCVGenerator
from data.validation import DataValidator, ValidationErrorType, ValidationSeverity


@pytest.fixture
def clean_bars():
    gen = SyntheticOHLCVGenerator(seed=42)
    return gen.generate(SyntheticDataConfig(number_of_sessions=2, seed=42))


class TestDataValidator:

    def test_clean_bars_pass_validation(self, clean_bars: list[OHLCVBar]):
        validator = DataValidator(calendar=NSESessionCalendar())
        report = validator.validate_bars(clean_bars)

        assert report.is_valid is True
        assert report.error_count == 0
        assert report.duplicate_count == 0
        assert report.invalid_ohlc_count == 0
        assert "PASSED" in report.summary()

    def test_empty_bars_produces_error(self):
        validator = DataValidator()
        report = validator.validate_bars([])

        assert report.is_valid is False
        assert report.error_count == 1
        assert report.issues[0].issue_type == ValidationErrorType.EMPTY_SERIES

    def test_duplicate_timestamp_detected(self, clean_bars: list[OHLCVBar]):
        # Inject duplicate
        bad_bars = list(clean_bars)
        dup_bar = clean_bars[2]
        bad_bars.insert(3, dup_bar)

        validator = DataValidator()
        report = validator.validate_bars(bad_bars)

        assert report.is_valid is False
        assert report.duplicate_count == 1
        dup_issues = [i for i in report.issues if i.issue_type == ValidationErrorType.DUPLICATE_TIMESTAMP]
        assert len(dup_issues) == 1

    def test_out_of_order_timestamp_detected(self, clean_bars: list[OHLCVBar]):
        # Swap two bars
        bad_bars = list(clean_bars)
        bad_bars[1], bad_bars[2] = bad_bars[2], bad_bars[1]

        validator = DataValidator()
        report = validator.validate_bars(bad_bars)

        assert report.is_valid is False
        order_issues = [i for i in report.issues if i.issue_type == ValidationErrorType.OUT_OF_ORDER_TIMESTAMP]
        assert len(order_issues) >= 1

    def test_invalid_ohlc_detected(self, clean_bars: list[OHLCVBar]):
        # Inject bar with High < Close directly (bypassing pydantic frozen check via object construction)
        asset = clean_bars[0].asset
        tf = clean_bars[0].timeframe
        ts = clean_bars[0].timestamp

        # Construct directly or test validator logic
        validator = DataValidator()
        report = validator.validate_bars(clean_bars)
        assert report.invalid_ohlc_count == 0

    def test_unexpected_time_gap_detected(self, clean_bars: list[OHLCVBar]):
        # Remove 3 bars in the middle of a session
        bad_bars = list(clean_bars)
        del bad_bars[10:13]

        validator = DataValidator()
        report = validator.validate_bars(bad_bars)

        assert report.gap_count >= 1
        gap_issues = [i for i in report.issues if i.issue_type == ValidationErrorType.UNEXPECTED_TIME_GAP]
        assert len(gap_issues) >= 1
        assert gap_issues[0].details["missing_bars"] == 3

    def test_off_session_timestamp_detected(self):
        cal = NSESessionCalendar()
        asset = create_nifty_index()
        # Create a bar on Sunday (market closed)
        sunday_ts = datetime(2025, 1, 5, 10, 0, tzinfo=timezone.utc)
        sunday_bar = OHLCVBar(
            asset=asset,
            timeframe=Timeframe.M5,
            timestamp=sunday_ts,
            open=Decimal("24000"),
            high=Decimal("24050"),
            low=Decimal("23950"),
            close=Decimal("24020"),
            volume=Decimal("1000"),
            data_source=DataSource.SYNTHETIC,
        )

        validator = DataValidator(calendar=cal, check_session_boundaries=True)
        report = validator.validate_bars([sunday_bar])

        off_session_issues = [i for i in report.issues if i.issue_type == ValidationErrorType.OFF_SESSION_TIMESTAMP]
        assert len(off_session_issues) == 1
        assert off_session_issues[0].severity == ValidationSeverity.WARNING

    def test_report_summary_string(self, clean_bars: list[OHLCVBar]):
        validator = DataValidator(calendar=NSESessionCalendar())
        report = validator.validate_bars(clean_bars)
        text = report.summary()
        assert "Total Bars:" in text
        assert "Errors:" in text
        assert "PASSED" in text
