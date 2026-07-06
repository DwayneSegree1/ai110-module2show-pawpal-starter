from datetime import time

import streamlit as st

from pawpal_system import (
    Owner,
    Pet,
    Priority,
    ScheduleConstraints,
    Scheduler,
    Task,
    TaskType,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to PawPal+ — add an owner, a pet, and some care tasks below, then generate
today's schedule.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# The Owner instance must survive across reruns, so it lives in st.session_state
# instead of being recreated as a local variable on every script run.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", email="jordan@example.com")

owner = st.session_state.owner

st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)
owner.email = st.text_input("Owner email", value=owner.email)

st.subheader("Add a Pet")
col1, col2, col3 = st.columns(3)
with col1:
    pet_name = st.text_input("Pet name", value="Mochi")
with col2:
    species = st.selectbox("Species", ["dog", "cat", "other"])
with col3:
    age = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

if st.button("Add pet"):
    if owner.get_pet(pet_name) is None:
        owner.add_pet(Pet(name=pet_name, species=species, breed="", age=int(age), owner=owner))
        st.success(f"Added {pet_name}.")
    else:
        st.warning(f"{pet_name} has already been added.")

if not owner.pets:
    st.info("No pets yet. Add one above.")
    st.stop()

st.write("Pets:", ", ".join(pet.name for pet in owner.pets))
selected_pet_name = st.selectbox("Selected pet", [pet.name for pet in owner.pets])
pet = owner.get_pet(selected_pet_name)

st.divider()

st.markdown("### Tasks")
st.caption("Add care tasks for the selected pet.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_type = st.selectbox("Type", [t.value for t in TaskType])
with col3:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col4:
    priority = st.selectbox("Priority", [p.value for p in Priority], index=2)

if st.button("Add task"):
    pet.add_task(
        Task(
            title=task_title,
            task_type=TaskType(task_type),
            duration_minutes=int(duration),
            priority=Priority(priority),
        )
    )
    st.success(f"Added '{task_title}' to {pet.name}.")

if pet.tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "title": t.title,
                "type": t.task_type.value,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.value,
            }
            for t in pet.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not pet.tasks:
        st.warning(f"{pet.name} has no tasks yet. Add one above first.")
    else:
        constraints = ScheduleConstraints(
            day_start=time(7, 0), day_end=time(20, 0), max_available_minutes=480
        )
        plan = Scheduler().build_schedule(pet, constraints)
        st.text(plan.summary())
