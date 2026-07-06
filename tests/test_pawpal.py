from datetime import date, datetime, time

from pawpal_system import (
    DailyPlan,
    Owner,
    Pet,
    Priority,
    Recurrence,
    ScheduledTask,
    Scheduler,
    Task,
    TaskType,
    TimeWindow,
)


def make_pet():
    owner = Owner(name="Jordan", email="jordan@example.com")
    pet = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3, owner=owner)
    owner.add_pet(pet)
    return pet


def test_mark_completed_changes_task_status():
    task = Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
    )
    assert task.last_completed_at is None

    completed_at = datetime(2026, 7, 6, 8, 30)
    task.mark_completed(completed_at)

    assert task.last_completed_at == completed_at


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.tasks) == 0

    task = Task(
        title="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
    )
    pet.add_task(task)

    assert len(pet.tasks) == 1
    assert task in pet.tasks


# --- Sorting Correctness ---------------------------------------------------


def test_sort_by_time_returns_chronological_order():
    pet = make_pet()
    morning = Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.LOW,
        preferred_window=TimeWindow(start_time=time(8, 0), end_time=time(8, 30)),
    )
    evening = Task(
        title="Evening walk",
        task_type=TaskType.WALK,
        duration_minutes=20,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(18, 0), end_time=time(18, 20)),
    )
    breakfast = Task(
        title="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.MEDIUM,
        preferred_window=TimeWindow(start_time=time(9, 0), end_time=time(9, 10)),
    )

    # Added out of chronological order, with priority deliberately misaligned
    # with time order, to confirm sort_by_time() ignores priority entirely.
    pet.add_task(evening)
    pet.add_task(morning)
    pet.add_task(breakfast)

    ordered = Scheduler().sort_by_time(pet.tasks)

    assert [t.title for t in ordered] == ["Morning walk", "Breakfast", "Evening walk"]


def test_sort_by_time_places_tasks_without_window_last():
    scheduled = Task(
        title="Scheduled",
        task_type=TaskType.WALK,
        duration_minutes=10,
        priority=Priority.LOW,
        preferred_window=TimeWindow(start_time=time(7, 0), end_time=time(7, 10)),
    )
    unscheduled = Task(
        title="Unscheduled",
        task_type=TaskType.OTHER,
        duration_minutes=10,
        priority=Priority.HIGH,
    )

    ordered = Scheduler().sort_by_time([unscheduled, scheduled])

    assert [t.title for t in ordered] == ["Scheduled", "Unscheduled"]


# --- Recurrence Logic --------------------------------------------------


def test_mark_completed_daily_task_creates_task_for_next_day():
    task = Task(
        title="Give medication",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=Priority.HIGH,
        recurrence=Recurrence.DAILY,
    )
    completed_at = datetime(2026, 7, 6, 9, 0)

    next_task = task.mark_completed(completed_at)

    assert next_task is not None
    assert next_task is not task
    assert next_task.title == task.title
    assert next_task.recurrence == Recurrence.DAILY
    assert next_task.due_date == date(2026, 7, 7)


def test_mark_completed_non_recurring_task_returns_none():
    task = Task(
        title="Vet checkup",
        task_type=TaskType.OTHER,
        duration_minutes=30,
        priority=Priority.MEDIUM,
    )

    next_task = task.mark_completed(datetime(2026, 7, 6, 9, 0))

    assert next_task is None


# --- Conflict Detection -----------------------------------------------


def test_check_for_conflicts_flags_overlapping_times():
    pet = make_pet()
    plan = DailyPlan(plan_date=date(2026, 7, 6), pet=pet)

    walk = Task(title="Walk", task_type=TaskType.WALK, duration_minutes=30, priority=Priority.HIGH)
    vet_visit = Task(title="Vet visit", task_type=TaskType.OTHER, duration_minutes=30, priority=Priority.HIGH)
    plan.entries.append(ScheduledTask(task=walk, start_time=time(8, 0), end_time=time(8, 30)))
    plan.entries.append(ScheduledTask(task=vet_visit, start_time=time(8, 15), end_time=time(8, 45)))

    warnings = Scheduler().check_for_conflicts([plan])

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Vet visit" in warnings[0]


def test_check_for_conflicts_no_warning_for_non_overlapping_times():
    pet = make_pet()
    plan = DailyPlan(plan_date=date(2026, 7, 6), pet=pet)

    walk = Task(title="Walk", task_type=TaskType.WALK, duration_minutes=30, priority=Priority.HIGH)
    breakfast = Task(title="Breakfast", task_type=TaskType.FEEDING, duration_minutes=10, priority=Priority.HIGH)
    plan.entries.append(ScheduledTask(task=walk, start_time=time(8, 0), end_time=time(8, 30)))
    plan.entries.append(ScheduledTask(task=breakfast, start_time=time(9, 0), end_time=time(9, 10)))

    warnings = Scheduler().check_for_conflicts([plan])

    assert warnings == []
