from datetime import datetime, time

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    Recurrence,
    ScheduleConstraints,
    Scheduler,
    Task,
    TaskType,
    TimeWindow,
)


def main():
    owner = Owner(name="Jordan", email="jordan@example.com")

    biscuit = Pet(name="Biscuit", species="dog", breed="Golden Retriever", age=3, owner=owner)
    mochi = Pet(name="Mochi", species="cat", breed="Domestic Shorthair", age=2, owner=owner)
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    morning_walk = Task(
        title="Morning walk",
        task_type=TaskType.WALK,
        duration_minutes=30,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(8, 0), end_time=time(8, 30)),
    )
    breakfast = Task(
        title="Breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=10,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(9, 0), end_time=time(9, 10)),
    )
    evening_walk = Task(
        title="Evening walk",
        task_type=TaskType.WALK,
        duration_minutes=20,
        priority=Priority.MEDIUM,
        preferred_window=TimeWindow(start_time=time(18, 0), end_time=time(18, 20)),
    )
    litter_box = Task(
        title="Clean litter box",
        task_type=TaskType.OTHER,
        duration_minutes=15,
        priority=Priority.MEDIUM,
        preferred_window=TimeWindow(start_time=time(10, 0), end_time=time(10, 15)),
    )
    mochi_feeding = Task(
        title="Mochi breakfast",
        task_type=TaskType.FEEDING,
        duration_minutes=5,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(7, 30), end_time=time(7, 35)),
    )
    # Same time as Biscuit's morning_walk, same pet -> should trigger a same-pet conflict warning.
    vet_checkup = Task(
        title="Vet checkup",
        task_type=TaskType.OTHER,
        duration_minutes=30,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(8, 0), end_time=time(8, 30)),
    )
    # Same time as Biscuit's morning_walk, different pet -> should trigger a cross-pet conflict warning.
    mochi_outdoor_time = Task(
        title="Mochi outdoor time",
        task_type=TaskType.ENRICHMENT,
        duration_minutes=30,
        priority=Priority.HIGH,
        preferred_window=TimeWindow(start_time=time(8, 0), end_time=time(8, 30)),
    )

    # Added deliberately out of chronological order to exercise sort_by_time().
    biscuit.add_task(breakfast)
    biscuit.add_task(evening_walk)
    biscuit.add_task(morning_walk)
    biscuit.add_task(vet_checkup)
    mochi.add_task(litter_box)
    mochi.add_task(mochi_feeding)
    mochi.add_task(mochi_outdoor_time)

    # Mark one task complete so filter_by_completion() has something to split on.
    breakfast.mark_completed(datetime.now())

    constraints = ScheduleConstraints(day_start=time(7, 0), day_end=time(20, 0), max_available_minutes=180)
    scheduler = Scheduler()

    plans = []
    for pet in owner.pets:
        plan = scheduler.build_schedule(pet, constraints)
        plans.append(plan)
        print(plan.summary())
        print()

    print("--- Conflict Detection: check_for_conflicts() ---")
    conflicts = scheduler.check_for_conflicts(plans)
    if conflicts:
        for warning in conflicts:
            print(f"WARNING: {warning}")
    else:
        print("No conflicts detected.")
    print()

    print("--- Sorting Logic: sort_by_time() ---")
    for pet in owner.pets:
        ordered = scheduler.sort_by_time(pet.tasks)
        times = ", ".join(
            f"{t.title} ({t.preferred_window.start_time.strftime('%H:%M')})" for t in ordered
        )
        print(f"{pet.name}: {times}")
    print()

    print("--- Filtering Logic: filter_by_completion() ---")
    all_tasks = biscuit.tasks + mochi.tasks
    done = scheduler.filter_by_completion(all_tasks, completed=True)
    pending = scheduler.filter_by_completion(all_tasks, completed=False)
    print("Completed:", ", ".join(t.title for t in done) or "none")
    print("Pending:", ", ".join(t.title for t in pending) or "none")
    print()

    print("--- Filtering Logic: filter_by_pet() ---")
    for pet_name in ("Biscuit", "Mochi"):
        pet_tasks = scheduler.filter_by_pet(owner, pet_name)
        print(f"{pet_name}: {', '.join(t.title for t in pet_tasks) or 'none'}")
    print()

    print("--- Recurrence Logic: mark_completed() spawns the next occurrence ---")
    daily_task = Task(
        title="Give medication",
        task_type=TaskType.MEDICATION,
        duration_minutes=5,
        priority=Priority.HIGH,
        recurrence=Recurrence.DAILY,
    )
    weekly_task = Task(
        title="Grooming",
        task_type=TaskType.GROOMING,
        duration_minutes=45,
        priority=Priority.LOW,
        recurrence=Recurrence.WEEKLY,
    )
    biscuit.add_task(daily_task)
    biscuit.add_task(weekly_task)

    completed_at = datetime.now()
    for task in (daily_task, weekly_task):
        next_task = task.mark_completed(completed_at)
        if next_task is not None:
            biscuit.add_task(next_task)
            print(f"'{task.title}' completed {completed_at.date()} -> next due {next_task.due_date}")


if __name__ == "__main__":
    main()
