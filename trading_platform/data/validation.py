"""
Market data validator and quality report engine.

Detects:
- Missing timestamps (compared against expected session intervals)
- Duplicate timestamps
- Invalid OHLC relationships (High < Open/Close, Low > Open/Close, Low > High)
- Negative volume
- Zero or negative prices
- Timezone inconsistencies (naive datetimes)
- Unordered timestamps
- Unexpected intraday time gaps
- Off-session timestamps

Produces structured, immutable ValidationReport objects rather than mutating data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Any, Optional

from core.enums import Timeframe
from core.models import Asset, OHLCVBar
from data.sessions import SessionCalendar, _timeframe_to_timedelta


class ValidationErrorType(str, Enum):
    """Specific categories of data quality flaws."""
    EMPTY_SERIES = "EMPTY_SERIES"
    TIMEZONE_INCONSISTENT = "TIMEZONE_INCONSISTENT"
    DUPLICATE_TIMESTAMP = "DUPLICATE_TIMESTAMP"
    OUT_OF_ORDER_TIMESTAMP = "OUT_OF_ORDER_TIMESTAMP"
    INVALID_OHLC_RELATIONSHIP = "INVALID_OHLC_RELATIONSHIP"
    NON_POSITIVE_PRICE = "NON_POSITIVE_PRICE"
    NEGATIVE_VOLUME = "NEGATIVE_VOLUME"
    UNEXPECTED_TIME_GAP = "UNEXPECTED_TIME_GAP"
    OFF_SESSION_TIMESTAMP = "OFF_SESSION_TIMESTAMP"
    MISSING_TIMESTAMPS = "MISSING_TIMESTAMPS"


class ValidationSeverity(str, Enum):
    """Severity level of an identified data issue."""
    ERROR = "ERROR"       # Data cannot be safely used for trading or backtesting
    WARNING = "WARNING"   # Anomaly present, but may be acceptable (e.g. market halt)


@dataclass(frozen=True)
class ValidationIssue:
    """An individual recorded issue found in a dataset."""

    issue_type: ValidationErrorType
    severity: ValidationSeverity
    message: str
    bar_index: Optional[int] = None
    timestamp: Optional[datetime] = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationReport:
    """Comprehensive data quality report for a bar collection."""

    asset: Optional[Asset]
    timeframe: Optional[Timeframe]
    total_bars: int
    issues: list[ValidationIssue] = field(default_factory=list)
    missing_bar_count: int = 0
    duplicate_count: int = 0
    invalid_ohlc_count: int = 0
    gap_count: int = 0

    @property
    def error_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)

    @property
    def is_valid(self) -> bool:
        """Data is valid if zero ERROR-level issues were found."""
        return self.error_count == 0

    @property
    def is_perfect(self) -> bool:
        """Data is completely clean with zero errors and zero warnings."""
        return len(self.issues) == 0

    def summary(self) -> str:
        """Produce a human-readable diagnostic text summary."""
        status = "PASSED" if self.is_valid else "FAILED"
        lines = [
            f"Data Quality Report: {status}",
            f"  Total Bars:        {self.total_bars}",
            f"  Errors:            {self.error_count}",
            f"  Warnings:          {self.warning_count}",
            f"  Duplicate Bars:    {self.duplicate_count}",
            f"  Missing Bars:      {self.missing_bar_count}",
            f"  Invalid OHLC:      {self.invalid_ohlc_count}",
            f"  Unexpected Gaps:   {self.gap_count}",
        ]
        if self.issues:
            lines.append("  Issues Sample (first 10):")
            for iss in self.issues[:10]:
                ts_str = iss.timestamp.isoformat() if iss.timestamp else "N/A"
                lines.append(f"    [{iss.severity.value}] idx={iss.bar_index} ts={ts_str} {iss.issue_type.value}: {iss.message}")
        return "\n".join(lines)


class DataValidator:
    """
    Validates series of OHLCV bars against financial consistency rules and session boundaries.
    """

    def __init__(
        self,
        calendar: Optional[SessionCalendar] = None,
        check_session_boundaries: bool = True,
        max_reported_issues: int = 500,
    ) -> None:
        self.calendar = calendar
        self.check_session_boundaries = check_session_boundaries
        self.max_reported_issues = max_reported_issues

    def validate_bars(
        self,
        bars: list[OHLCVBar],
        calendar: Optional[SessionCalendar] = None,
    ) -> ValidationReport:
        """
        Execute full validation suite across the bar series.

        Args:
            bars: List of OHLCVBar instances.
            calendar: Optional SessionCalendar override.

        Returns:
            ValidationReport detailing all issues and pass/fail status.
        """
        active_cal = calendar or self.calendar
        total = len(bars)
        if total == 0:
            return ValidationReport(
                asset=None,
                timeframe=None,
                total_bars=0,
                issues=[
                    ValidationIssue(
                        issue_type=ValidationErrorType.EMPTY_SERIES,
                        severity=ValidationSeverity.ERROR,
                        message="Bar dataset is empty",
                    )
                ],
            )

        asset = bars[0].asset
        timeframe = bars[0].timeframe
        step = _timeframe_to_timedelta(timeframe)

        issues: list[ValidationIssue] = []
        dup_count = 0
        invalid_ohlc_count = 0
        gap_count = 0
        seen_timestamps: set[datetime] = set()

        for idx, bar in enumerate(bars):
            ts = bar.timestamp

            # 1. Timezone awareness check
            if ts.tzinfo is None:
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationErrorType.TIMEZONE_INCONSISTENT,
                        severity=ValidationSeverity.ERROR,
                        message="Timestamp lacks timezone information",
                        bar_index=idx,
                        timestamp=ts,
                    )
                )

            # 2. Duplicate timestamp check
            if ts in seen_timestamps:
                dup_count += 1
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationErrorType.DUPLICATE_TIMESTAMP,
                        severity=ValidationSeverity.ERROR,
                        message=f"Duplicate timestamp encountered: {ts.isoformat()}",
                        bar_index=idx,
                        timestamp=ts,
                    )
                )
            else:
                seen_timestamps.add(ts)

            # 3. Chronological order & Gap check
            if idx > 0:
                prev_ts = bars[idx - 1].timestamp
                if ts < prev_ts:
                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationErrorType.OUT_OF_ORDER_TIMESTAMP,
                            severity=ValidationSeverity.ERROR,
                            message=f"Bar timestamp {ts.isoformat()} precedes previous {prev_ts.isoformat()}",
                            bar_index=idx,
                            timestamp=ts,
                        )
                    )
                elif ts > prev_ts:
                    diff = ts - prev_ts
                    # If within the same day and diff exceeds step
                    if prev_ts.date() == ts.date() and diff > step:
                        gap_count += 1
                        missed = int((diff / step) - 1)
                        issues.append(
                            ValidationIssue(
                                issue_type=ValidationErrorType.UNEXPECTED_TIME_GAP,
                                severity=ValidationSeverity.WARNING,
                                message=f"Intraday time gap of {diff} ({missed} bars missing)",
                                bar_index=idx,
                                timestamp=ts,
                                details={"gap_duration_seconds": diff.total_seconds(), "missing_bars": missed},
                            )
                        )

            # 4. Non-positive price check
            for price_name, val in [("open", bar.open), ("high", bar.high), ("low", bar.low), ("close", bar.close)]:
                if val <= 0:
                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationErrorType.NON_POSITIVE_PRICE,
                            severity=ValidationSeverity.ERROR,
                            message=f"{price_name} price ({val}) is non-positive",
                            bar_index=idx,
                            timestamp=ts,
                        )
                    )

            # 5. OHLC relationship checks
            if (bar.high < bar.open) or (bar.high < bar.close) or (bar.low > bar.open) or (bar.low > bar.close) or (bar.low > bar.high):
                invalid_ohlc_count += 1
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationErrorType.INVALID_OHLC_RELATIONSHIP,
                        severity=ValidationSeverity.ERROR,
                        message=f"Impossible candle: O={bar.open}, H={bar.high}, L={bar.low}, C={bar.close}",
                        bar_index=idx,
                        timestamp=ts,
                    )
                )

            # 6. Negative volume check
            if bar.volume < 0:
                issues.append(
                    ValidationIssue(
                        issue_type=ValidationErrorType.NEGATIVE_VOLUME,
                        severity=ValidationSeverity.ERROR,
                        message=f"Negative volume ({bar.volume})",
                        bar_index=idx,
                        timestamp=ts,
                    )
                )

            # 7. Off-session check
            if active_cal and self.check_session_boundaries and ts.tzinfo is not None:
                if not active_cal.is_market_open(ts):
                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationErrorType.OFF_SESSION_TIMESTAMP,
                            severity=ValidationSeverity.WARNING,
                            message=f"Timestamp {ts.isoformat()} is outside active market sessions",
                            bar_index=idx,
                            timestamp=ts,
                        )
                    )

            if len(issues) >= self.max_reported_issues:
                break

        # 8. Check against expected session calendar timestamps for overall missing bars
        missing_bar_count = 0
        if active_cal and total > 0 and bars[0].timestamp.tzinfo is not None:
            first_ts = bars[0].timestamp
            last_ts = bars[-1].timestamp
            try:
                expected_ts_list = active_cal.expected_bar_timestamps(first_ts, last_ts, timeframe)
                actual_ts_set = {b.timestamp.astimezone(timezone.utc) for b in bars}
                missing_from_schedule = [e for e in expected_ts_list if e not in actual_ts_set]
                missing_bar_count = len(missing_from_schedule)
                if missing_bar_count > 0:
                    issues.append(
                        ValidationIssue(
                            issue_type=ValidationErrorType.MISSING_TIMESTAMPS,
                            severity=ValidationSeverity.WARNING,
                            message=f"{missing_bar_count} expected session bars are missing from dataset",
                            details={"missing_count": missing_bar_count},
                        )
                    )
            except Exception:
                pass

        return ValidationReport(
            asset=asset,
            timeframe=timeframe,
            total_bars=total,
            issues=issues,
            missing_bar_count=missing_bar_count,
            duplicate_count=dup_count,
            invalid_ohlc_count=invalid_ohlc_count,
            gap_count=gap_count,
        )
