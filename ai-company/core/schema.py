"""Frozen data records shared by every department.

All sim times are integers: whole simulated days since simulation day 0
(see ``core.clock.SimClock``).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Optional

TOPIC_RE = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_.]*$")

TASK_STATUSES = ("todo", "in_progress", "blocked", "done", "cancelled")
TASK_PRIORITIES = ("low", "medium", "high", "critical")
LEVELS = ("analyst", "consultant", "senior_consultant", "manager", "principal", "partner", "head", "executive")


@dataclass(frozen=True)
class Message:
    """A message on the bus.

    recipient is a department id (direct message) or ``"*"`` (deliver to every
    subscriber of ``topic``). ``topic`` is ``<publisher_dept>.<event>``.
    """

    id: str
    sender: str
    recipient: str
    topic: str
    body: dict = field(default_factory=dict)
    sim_time: int = 0
    reply_to: Optional[str] = None

    def __post_init__(self) -> None:
        if not TOPIC_RE.match(self.topic):
            raise ValueError(f"invalid topic name: {self.topic!r}")
        if not isinstance(self.body, dict):
            raise TypeError("Message.body must be a dict")
        if not self.id or not self.sender or not self.recipient:
            raise ValueError("Message id, sender and recipient are required")

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id, "sender": self.sender, "recipient": self.recipient,
            "topic": self.topic, "body": self.body, "sim_time": self.sim_time,
            "reply_to": self.reply_to,
        }


@dataclass(frozen=True)
class Task:
    id: str
    title: str
    owner: str
    status: str = "todo"
    priority: str = "medium"
    due: Optional[int] = None  # sim day (int) or None
    depends_on: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.status not in TASK_STATUSES:
            raise ValueError(f"invalid task status {self.status!r}; use one of {TASK_STATUSES}")
        if self.priority not in TASK_PRIORITIES:
            raise ValueError(f"invalid task priority {self.priority!r}; use one of {TASK_PRIORITIES}")
        object.__setattr__(self, "depends_on", tuple(self.depends_on))


@dataclass(frozen=True)
class Kpi:
    name: str
    unit: str
    target: float
    actual: Optional[float] = None
    higher_is_better: bool = True

    @property
    def attainment(self) -> Optional[float]:
        """actual/target for higher-is-better, target/actual for lower-is-better."""
        if self.actual is None:
            return None
        if self.higher_is_better:
            return self.actual / self.target if self.target else None
        return self.target / self.actual if self.actual else None

    @property
    def on_track(self) -> Optional[bool]:
        a = self.attainment
        return None if a is None else a >= 1.0


@dataclass(frozen=True)
class Role:
    """A role in a department's org chart.

    headcount_plan: (year1, year2, year3) year-end humans in this role.
    salary_band_gbp: (min, max) annual base salary in GBP (see COMPANY.md section 10).
    reports_to: title of the manager role (None for the CEO).
    """

    title: str
    department: str
    level: str
    headcount_plan: tuple[int, int, int] = (1, 1, 1)
    salary_band_gbp: tuple[int, int] = (0, 0)
    reports_to: Optional[str] = None

    def __post_init__(self) -> None:
        if len(self.headcount_plan) != 3:
            raise ValueError("headcount_plan must be (year1, year2, year3)")
        if len(self.salary_band_gbp) != 2 or self.salary_band_gbp[0] > self.salary_band_gbp[1]:
            raise ValueError("salary_band_gbp must be (min, max) with min <= max")
        object.__setattr__(self, "headcount_plan", tuple(self.headcount_plan))
        object.__setattr__(self, "salary_band_gbp", tuple(self.salary_band_gbp))
