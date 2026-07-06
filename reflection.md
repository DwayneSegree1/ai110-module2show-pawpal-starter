# PawPal+ Project Reflection

## 1. System Design
##  A user should be able to add pet information, schedule walks, see alll the task that are schedule for today
## and see when last the pet was fed

**a. Initial design**

My initial UML design (`diagrams/uml.mmd`) splits the system into data/model classes that hold pet-care information, enums/value objects that constrain that data, and service classes that turn the data into a schedule.

- **Owner** — stores the owner's name, email, and preferences, and owns a list of `Pet`s.
- **Pet** — stores name, species, breed, age, and its list of `Task`s; also exposes `get_last_completed()` so the app can answer "when was this pet last fed?"
- **Task** — represents one care task (title, `TaskType`, `duration_minutes`, `Priority`, whether it's `recurring`, an optional preferred `TimeWindow`, and `last_completed_at`); `mark_completed()` updates that timestamp.
- **TaskType** (enum) — categorizes a task (walk, feeding, medication, grooming, enrichment, other).
- **Priority** (enum) — low/medium/high, used to rank tasks.
- **TimeWindow** — a simple start/end time range a task prefers to happen in.
- **ScheduleConstraints** — the day's available start/end time, max available minutes, and owner preferences the scheduler must respect.
- **Scheduler** — the service that takes a `Pet`'s tasks plus `ScheduleConstraints`, ranks tasks by priority (`rank_tasks`), and produces a `DailyPlan`; `explain()` generates the reasoning text for a given entry.
- **DailyPlan** — the output for a given date/pet: a list of `ScheduledTask` entries, with `total_duration()` and `summary()` for display.
- **ScheduledTask** — one entry in the plan: the underlying `Task`, its assigned start/end time, and a `reason` string explaining why it was placed there.

The responsibilities are split so that `Task`/`Pet`/`Owner` only hold state, `Scheduler` owns all the decision-making logic, and `DailyPlan`/`ScheduledTask` are just the display-ready result — keeping the scheduling algorithm isolated from both data storage and the UI.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

In pawpal_system.py I fixed four structural gaps: Scheduler.build_schedule now takes (pet, constraints) instead of also taking a separate tasks list (removing the redundant/ambiguous duplicate of pet.tasks); Pet gained a current_plan field so today's generated schedule can be stored and re-read instead of recomputed; ScheduledTask gained an overlaps(other) stub to give time-conflict checking a defined home; and the Owner.add_pet() relationship is now intended to be the single place that keeps Pet.owner and Owner.pets in sync. All added methods are still empty (pass) — only the structure/signatures changed, no scheduling logic was implemented.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
