# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Today's Schedule for Biscuit (2026-07-06):
  08:00-08:30 Morning walk [high] - priority=high, duration=30min
  09:00-09:10 Breakfast [high] - priority=high, duration=10min

Today's Schedule for Mochi (2026-07-06):
  10:00-10:15 Clean litter box [medium] - priority=medium, duration=15min

```
# e.g.:
# Daily plan for Biscuit (Golden Retriever):
#   08:00 — Morning walk (30 min) [priority: high]
#   09:00 — Feeding (10 min) [priority: high]
#   ...
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
# Paste your pytest output here
```

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.rank_tasks()`, `Scheduler.sort_by_time()` | `rank_tasks()` orders tasks by priority (high → low), breaking ties by preferred start time — this is what `build_schedule()` uses to decide fit order. `sort_by_time()` orders tasks purely by preferred start time, ignoring priority, for a simple chronological view. |
| Filtering | `Scheduler.filter_by_completion()`, `Scheduler.filter_by_pet()` | `filter_by_completion(tasks, completed)` splits a task list into done/pending based on `Task.last_completed_at`. `filter_by_pet(owner, pet_name)` returns just the named pet's tasks via `Owner.get_pet()`. |
| Conflict handling | `DailyPlan.add_entry()`, `Scheduler.check_for_conflicts()` | `add_entry()` prevents a pet's own plan from holding two overlapping entries (skipped tasks are recorded in `DailyPlan.warnings` instead of vanishing silently). `check_for_conflicts(plans)` does a lightweight pairwise scan across one or more pets' plans and returns warning strings for any overlapping time slots — same pet or different pets sharing one owner — without raising or crashing. |
| Recurring tasks | `Task.mark_completed()`, `Task.next_occurrence()` | Each `Task` has a `recurrence` (`NONE`/`DAILY`/`WEEKLY`). Calling `mark_completed(timestamp)` records completion and automatically spawns the next occurrence via `next_occurrence()`, which uses `datetime.timedelta` (`+1 day` or `+7 days`) to compute the new `due_date` — handling month/year rollovers for free. |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
