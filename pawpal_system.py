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


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


_RECURRENCE_INTERVALS = {
    Recurrence.DAILY: timedelta(days=1),
    Recurrence.WEEKLY: timedelta(days=7),
}


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
    recurrence: Recurrence = Recurrence.NONE
    preferred_window: TimeWindow | None = None
    due_date: date | None = None
    last_completed_at: datetime | None = field(default=None, init=False)

    def mark_completed(self, timestamp: datetime) -> "Task | None":
        """Record completion and, for daily/weekly tasks, spawn the next occurrence.

        Args:
            timestamp: When the task was completed. Used as the base date for
                calculating the next occurrence's due date.

        Returns:
            A new Task representing the next occurrence if this task recurs
            (daily or weekly), otherwise None.
        """
        self.last_completed_at = timestamp
        return self.next_occurrence(timestamp.date())

    def next_occurrence(self, from_date: date | None = None) -> "Task | None":
        """Return a new Task for the next daily/weekly occurrence, or None if not recurring.

        Uses `datetime.timedelta` to advance `from_date` by one day (daily) or
        seven days (weekly), so calendar boundaries (month/year rollover) are
        handled automatically rather than computed by hand.

        Args:
            from_date: The date to advance from. Defaults to today if omitted.

        Returns:
            A copy of this task with an updated `due_date`, or None if this
            task's `recurrence` is `Recurrence.NONE`.
        """
        interval = _RECURRENCE_INTERVALS.get(self.recurrence)
        if interval is None:
            return None
        return Task(
            title=self.title,
            task_type=self.task_type,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            recurrence=self.recurrence,
            preferred_window=self.preferred_window,
            due_date=(from_date or date.today()) + interval,
        )


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
    warnings: list[str] = field(default_factory=list)

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
        for warning in self.warnings:
            lines.append(f"  WARNING: {warning}")
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
            except ValueError as exc:
                plan.warnings.append(str(exc))
                continue

            elapsed_minutes += task.duration_minutes

        pet.current_plan = plan
        return plan

    def check_for_conflicts(self, plans: list[DailyPlan]) -> list[str]:
        """Lightweight pairwise scan for entries that overlap in time.

        Compares every entry against every other entry across the given plans
        (whether from the same pet or different pets sharing one owner) and
        returns a warning message per overlap instead of raising, so callers
        can surface double-bookings without interrupting scheduling. This is
        an O(n^2) pairwise comparison rather than an interval-tree/sweep-line
        algorithm, which is intentional: task lists here are small enough
        that simplicity beats asymptotic optimality.

        Args:
            plans: One or more DailyPlans to check, possibly for different pets.

        Returns:
            A list of human-readable warning strings, one per overlapping
            pair of entries. Empty if no conflicts are found.
        """
        tagged = [(plan.pet.name, entry) for plan in plans for entry in plan.entries]
        warnings = []
        for i, (pet_a, entry_a) in enumerate(tagged):
            for pet_b, entry_b in tagged[i + 1 :]:
                if entry_a.overlaps(entry_b):
                    warnings.append(
                        f"'{entry_a.task.title}' ({pet_a}, {entry_a.start_time.strftime('%H:%M')}-"
                        f"{entry_a.end_time.strftime('%H:%M')}) overlaps '{entry_b.task.title}' "
                        f"({pet_b}, {entry_b.start_time.strftime('%H:%M')}-{entry_b.end_time.strftime('%H:%M')})"
                    )
        return warnings

    def rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by priority, breaking ties by preferred start time."""
        return sorted(
            tasks,
            key=lambda t: (
                self._PRIORITY_ORDER[t.priority],
                t.preferred_window.start_time if t.preferred_window else time.max,
            ),
        )

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by their preferred start time, ignoring priority.

        Tasks without a `preferred_window` sort last, since they have no
        start time to compare.

        Args:
            tasks: Tasks to sort.

        Returns:
            A new list of tasks ordered earliest-to-latest start time.
        """
        return sorted(
            tasks,
            key=lambda t: t.preferred_window.start_time if t.preferred_window else time.max,
        )

    def filter_by_completion(self, tasks: list[Task], completed: bool) -> list[Task]:
        """Return the tasks whose completion status matches the given flag.

        Args:
            tasks: Tasks to filter.
            completed: True to keep tasks with a `last_completed_at` timestamp,
                False to keep tasks that haven't been completed yet.

        Returns:
            The subset of `tasks` matching the requested completion status.
        """
        return [t for t in tasks if (t.last_completed_at is not None) == completed]

    def filter_by_pet(self, owner: Owner, pet_name: str) -> list[Task]:
        """Return the tasks belonging to the named pet, if that pet exists.

        Args:
            owner: The owner whose pets are searched.
            pet_name: Name of the pet to look up (via `Owner.get_pet`).

        Returns:
            That pet's task list, or an empty list if no pet matches the name.
        """
        pet = owner.get_pet(pet_name)
        return list(pet.tasks) if pet else []

    def explain(self, entry: ScheduledTask) -> str:
        """Return a short human-readable reason this entry was scheduled."""
        return f"priority={entry.task.priority.value}, duration={entry.task.duration_minutes}min"
