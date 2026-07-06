from datetime import datetime

from pawpal_system import Owner, Pet, Priority, Task, TaskType


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
