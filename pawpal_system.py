"""PawPal+ system classes.

Class stubs generated from diagrams/uml.mmd. No scheduling logic yet —
fill in method bodies as you implement behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
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
        """Return True if the given time falls within this window."""
        return self.start_time <= t <= self.end_time


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
        """Record when this task was last completed."""
        self.last_completed_at = timestamp


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    owner: "Owner"
    tasks: list[Task] = field(default_factory=list)
    current_plan: "DailyPlan | None" = field(default=None, init=False)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet's task list."""
        self.tasks.remove(task)

    def get_last_completed(self, task_type: TaskType) -> datetime | None:
        """Return the most recent completion time for tasks of the given type."""
        completions = [
            t.last_completed_at
            for t in self.tasks
            if t.task_type == task_type and t.last_completed_at is not None
        ]
        return max(completions) if completions else None


@dataclass
class Owner:
    name: str
    email: str
    pets: list[Pet] = field(default_factory=list)
    preferences: dict = field(default_factory=dict)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner and keep the pet's owner reference in sync."""
        pet.owner = self
        self.pets.append(pet)

    def get_pet(self, name: str) -> Pet | None:
        """Return this owner's pet with the given name, if any."""
        return next((p for p in self.pets if p.name == name), None)


@dataclass
class ScheduledTask:
    task: Task
    start_time: time
    end_time: time
    reason: str = ""

    def overlaps(self, other: "ScheduledTask") -> bool:
        """Return True if this entry's time range overlaps another entry's."""
        return self.start_time < other.end_time and other.start_time < self.end_time


@dataclass
class DailyPlan:
    plan_date: date
    pet: Pet
    entries: list[ScheduledTask] = field(default_factory=list)

    def add_entry(self, entry: ScheduledTask) -> None:
        """Add a scheduled entry, raising if it conflicts with an existing one."""
        for existing in self.entries:
            if entry.overlaps(existing):
                raise ValueError(
                    f"'{entry.task.title}' conflicts with '{existing.task.title}'"
                )
        self.entries.append(entry)

    def total_duration(self) -> int:
        """Return the total scheduled minutes across all entries."""
        return sum(entry.task.duration_minutes for entry in self.entries)

    def summary(self) -> str:
        """Return a human-readable, time-ordered listing of this plan."""
        header = f"Today's Schedule for {self.pet.name} ({self.plan_date}):"
        lines = [header]
        for entry in sorted(self.entries, key=lambda e: e.start_time):
            lines.append(
                f"  {entry.start_time.strftime('%H:%M')}-{entry.end_time.strftime('%H:%M')} "
                f"{entry.task.title} [{entry.task.priority.value}] - {entry.reason}"
            )
        if len(lines) == 1:
            lines.append("  No tasks scheduled.")
        return "\n".join(lines)


class Scheduler:
    _PRIORITY_ORDER = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}

    def build_schedule(self, pet: Pet, constraints: ScheduleConstraints) -> DailyPlan:
        """Build today's DailyPlan for a pet, greedily fitting tasks by priority."""
        plan = DailyPlan(plan_date=date.today(), pet=pet)
        elapsed_minutes = 0

        for task in self.rank_tasks(pet.tasks):
            if elapsed_minutes + task.duration_minutes > constraints.max_available_minutes:
                continue

            start = task.preferred_window.start_time if task.preferred_window else constraints.day_start
            end = (datetime.combine(plan.plan_date, start) + timedelta(minutes=task.duration_minutes)).time()
            entry = ScheduledTask(task=task, start_time=start, end_time=end)
            entry.reason = self.explain(entry)

            try:
                plan.add_entry(entry)
            except ValueError:
                continue

            elapsed_minutes += task.duration_minutes

        pet.current_plan = plan
        return plan

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, breaking ties by preferred start time."""
        return sorted(
            tasks,
            key=lambda t: (
                self._PRIORITY_ORDER[t.priority],
                t.preferred_window.start_time if t.preferred_window else time.max,
            ),
        )

    def explain(self, entry: ScheduledTask) -> str:
        """Return a short human-readable reason this entry was scheduled."""
        return f"priority={entry.task.priority.value}, duration={entry.task.duration_minutes}min"
