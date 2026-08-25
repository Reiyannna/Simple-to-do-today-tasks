"""Pure task logic: creating tasks, and daily reset / expiry rules.

No GUI or file I/O here on purpose, so this module can be unit-tested
without touching Tkinter or the filesystem.
"""
from __future__ import annotations

import itertools
import uuid
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from typing import Optional


DATE_FMT = "%Y-%m-%d"


def today_str() -> str:
    return date.today().strftime(DATE_FMT)


def parse_date(s: str) -> date:
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


@dataclass
class Task:
    id: str
    name: str
    duration_days: int          # e.g. 1, 7, 30, 365
    start_date: str             # DATE_FMT string
    last_reset_date: str        # DATE_FMT string
    done_today: bool = False

    @staticmethod
    def new(name: str, duration_days: int) -> "Task":
        t = today_str()
        return Task(
            id=str(uuid.uuid4()),
            name=name,
            duration_days=duration_days,
            start_date=t,
            last_reset_date=t,
            done_today=False,
        )

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Task":
        return Task(
            id=d["id"],
            name=d["name"],
            duration_days=int(d["duration_days"]),
            start_date=d["start_date"],
            last_reset_date=d["last_reset_date"],
            done_today=bool(d.get("done_today", False)),
        )

    def expiry_date(self) -> date:
        return parse_date(self.start_date) + timedelta(days=self.duration_days)

    def days_left(self, as_of: Optional[date] = None) -> int:
        as_of = as_of or date.today()
        return (self.expiry_date() - as_of).days

    def is_expired(self, as_of: Optional[date] = None) -> bool:
        as_of = as_of or date.today()
        return as_of >= self.expiry_date()

    def needs_reset(self, as_of: Optional[date] = None) -> bool:
        as_of = as_of or date.today()
        return parse_date(self.last_reset_date) < as_of

    def apply_daily_reset(self, as_of: Optional[date] = None) -> None:
        """If it's a new day since the last reset, uncheck the task."""
        as_of = as_of or date.today()
        if self.needs_reset(as_of):
            self.done_today = False
            self.last_reset_date = as_of.strftime(DATE_FMT)


def process_tasks(tasks: list[Task], as_of: Optional[date] = None) -> list[Task]:
    """Apply daily reset to each task and drop any that have expired.

    Returns the surviving list of tasks (mutated in place where kept).
    """
    as_of = as_of or date.today()
    survivors = []
    for t in tasks:
        if t.is_expired(as_of):
            continue
        t.apply_daily_reset(as_of)
        survivors.append(t)
    return survivors


DURATION_PRESETS = [
    ("Today only", 1),
    ("1 week", 7),
    ("1 month", 30),
    ("1 year", 365),
]
