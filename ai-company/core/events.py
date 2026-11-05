"""Append-only event log with simple queries and JSONL export."""

from __future__ import annotations

import fnmatch
import json
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Callable, Iterator, Optional


@dataclass(frozen=True)
class Event:
    seq: int
    sim_time: int
    department: str
    topic: str
    summary: str
    data: dict = field(default_factory=dict)


class EventLog:
    def __init__(self, start: Optional[date] = None) -> None:
        self._events: list[Event] = []
        self.start = start

    def append(self, sim_time: int, department: str, topic: str, summary: str = "",
               data: Optional[dict] = None) -> Event:
        ev = Event(len(self._events), sim_time, department, topic, summary, dict(data or {}))
        self._events.append(ev)
        return ev

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self) -> Iterator[Event]:
        return iter(self._events)

    def __getitem__(self, i):
        return self._events[i]

    def query(self, department: Optional[str] = None, topic: Optional[str] = None,
              since: Optional[int] = None, until: Optional[int] = None,
              predicate: Optional[Callable[[Event], bool]] = None) -> list[Event]:
        """Filter events. ``topic`` may be an fnmatch pattern ('sales.*'). since/until are inclusive sim days."""
        out = []
        for ev in self._events:
            if department is not None and ev.department != department:
                continue
            if topic is not None and not fnmatch.fnmatchcase(ev.topic, topic):
                continue
            if since is not None and ev.sim_time < since:
                continue
            if until is not None and ev.sim_time > until:
                continue
            if predicate is not None and not predicate(ev):
                continue
            out.append(ev)
        return out

    def count_by(self, field_name: str = "department") -> dict[str, int]:
        counts: dict[str, int] = {}
        for ev in self._events:
            key = getattr(ev, field_name)
            counts[key] = counts.get(key, 0) + 1
        return dict(sorted(counts.items()))

    def to_dict(self, ev: Event) -> dict[str, Any]:
        d = {"seq": ev.seq, "sim_time": ev.sim_time, "department": ev.department,
             "topic": ev.topic, "summary": ev.summary, "data": ev.data}
        if self.start is not None:
            d["date"] = (self.start + timedelta(days=ev.sim_time)).isoformat()
        return d

    def to_jsonl(self, events: Optional[list[Event]] = None) -> str:
        """One JSON object per line, in append order (deterministic: sorted keys)."""
        evs = self._events if events is None else events
        return "".join(json.dumps(self.to_dict(e), sort_keys=True, default=str) + "\n" for e in evs)

    def write_jsonl(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_jsonl())
