"""PawPal+ system classes.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
fill in method bodies as you implement behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import Enum


class TaskType(Enum):
    WALK = "walk"
    FEEDING = "feeding"
    MEDICATION = "medication"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    OTHER = "other"


class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class TimeWindow:
    start_time: time
    end_time: time

    def contains(self, t: time) -> bool:
        pass


@dataclass
class ScheduleConstraints:
    day_start: time
    day_end: time
    max_available_minutes: int
    owner_preferences: dict = field(default_factory=dict)


@dataclass
class Task:
    title: str
    task_type: TaskType
    duration_minutes: int
    priority: Priority
    recurring: bool = False
    preferred_window: TimeWindow | None = None
    last_completed_at: datetime | None = field(default=None, init=False)

    def mark_completed(self, timestamp: datetime) -> None:
        pass


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    owner: "Owner"
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_last_completed(self, task_type: TaskType) -> datetime | None:
        pass


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pet(self, name: str) -> Pet | None:
        pass


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""


@dataclass
class DailyPlan:
    plan_date: date
    pet: Pet
    entries: list[ScheduledTask] = field(default_factory=list)

    def add_entry(self, entry: ScheduledTask) -> None:
        pass

    def total_duration(self) -> int:
        pass

    def summary(self) -> str:
        pass


class Scheduler:
    def build_schedule(
        self, pet: Pet, tasks: list[Task], constraints: ScheduleConstraints
    ) -> DailyPlan:
        pass

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def explain(self, entry: ScheduledTask) -> str:
        pass
