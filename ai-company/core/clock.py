"""Deterministic simulation clock. Day 0 is ``start`` (default Monday 2026-01-05)."""

from __future__ import annotations

from datetime import date, timedelta

DEFAULT_START = date(2026, 1, 5)
FIRST_FISCAL_YEAR = 2026  # Year 1 in COMPANY.md


class SimClock:
    def __init__(self, start: date = DEFAULT_START, days_per_tick: int = 1) -> None:
        if days_per_tick < 1:
            raise ValueError("days_per_tick must be >= 1")
        self.start = start
        self.days_per_tick = days_per_tick
        self._day = 0

    @property
    def day(self) -> int:
        """Whole simulated days since start (this is Message.sim_time)."""
        return self._day

    @property
    def tick(self) -> int:
        return self._day // self.days_per_tick

    @property
    def date(self) -> date:
        return self.date_of(self._day)

    def date_of(self, day: int) -> date:
        return self.start + timedelta(days=day)

    def day_of(self, d: date) -> int:
        return (d - self.start).days

    def advance(self, ticks: int = 1) -> int:
        """Advance by whole ticks; returns the new day."""
        if ticks < 0:
            raise ValueError("cannot move the clock backwards")
        self._day += ticks * self.days_per_tick
        return self._day

    def advance_days(self, days: int) -> int:
        if days < 0:
            raise ValueError("cannot move the clock backwards")
        self._day += days
        return self._day

    # convenience calendar helpers -------------------------------------
    @property
    def year_index(self) -> int:
        """1 for FY2026, 2 for FY2027, 3 for FY2028 (calendar-year fiscal years)."""
        return self.date.year - FIRST_FISCAL_YEAR + 1

    @property
    def quarter(self) -> int:
        return (self.date.month - 1) // 3 + 1

    @property
    def is_month_start(self) -> bool:
        return self.date.day == 1

    @property
    def is_weekday(self) -> bool:
        return self.date.weekday() < 5

    def every(self, days: int, offset: int = 0) -> bool:
        """True when the current day is a multiple of ``days`` (plus offset)."""
        return days > 0 and (self._day - offset) % days == 0

    def __repr__(self) -> str:
        return f"SimClock(day={self._day}, date={self.date.isoformat()})"
