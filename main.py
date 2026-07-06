from datetime import time

from pawpal_system import (
    Owner,
    Pet,
    Priority,
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
    litter_box = Task(
        title="Clean litter box",
        task_type=TaskType.OTHER,
        duration_minutes=15,
        priority=Priority.MEDIUM,
        preferred_window=TimeWindow(start_time=time(10, 0), end_time=time(10, 15)),
    )

    biscuit.add_task(morning_walk)
    biscuit.add_task(breakfast)
    mochi.add_task(litter_box)

    constraints = ScheduleConstraints(day_start=time(7, 0), day_end=time(20, 0), max_available_minutes=180)
    scheduler = Scheduler()

    for pet in owner.pets:
        plan = scheduler.build_schedule(pet, constraints)
        print(plan.summary())
        print()


if __name__ == "__main__":
    main()
