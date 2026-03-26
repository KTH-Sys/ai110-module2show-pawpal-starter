# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The initial UML design includes four core classes:

- **Task** (dataclass): Represents a single pet care activity with attributes for title, time (HH:MM), duration, priority (high/medium/low), frequency (once/daily/weekly), and completion status. Responsible for tracking its own state via `mark_complete()`.
- **Pet** (dataclass): Stores a pet's name, species, and a list of associated Tasks. Responsible for adding/removing tasks and tagging them with the pet's name.
- **Owner** (dataclass): Manages multiple Pets and provides a method to collect all tasks across pets via `get_all_tasks()`.
- **Scheduler**: The scheduling brain that retrieves tasks from the Owner, then sorts, filters, detects conflicts, handles recurrence, and generates a prioritized daily schedule.

Relationships: Owner has many Pets (1-to-many), Pet has many Tasks (1-to-many), Scheduler references one Owner.

Three core user actions identified:
1. Add a pet with name and species
2. Schedule a task (walk, feeding, meds) with time, priority, and frequency
3. View today's schedule sorted by priority/time with conflict warnings

**b. Design changes**

During implementation, the Scheduler gained more responsibility than initially planned. Originally, `mark_complete()` was only on the Task class. However, to support automatic recurring task creation, the Scheduler needed a `mark_task_complete()` wrapper that both completes the task and generates the next occurrence for the correct pet. This meant the Scheduler needed to know about the Owner's pets — a tighter coupling than the UML suggested, but necessary for the recurrence feature to work cleanly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Priority**: Tasks are sorted high → medium → low so urgent care (medications, walks) comes first.
- **Time**: Within each priority level, tasks are ordered chronologically by their HH:MM time slot.
- **Frequency**: Daily and weekly tasks automatically regenerate after completion, ensuring recurring care isn't forgotten.
- **Conflicts**: The scheduler detects when two tasks share the same time slot and issues warnings.

Priority was chosen as the primary sort key because missing a high-priority task (like medication) has more consequence than missing a low-priority one (like playtime).

**b. Tradeoffs**

The conflict detection only checks for exact time matches (e.g., two tasks both at "08:00") rather than overlapping durations (e.g., a 30-minute task at 07:45 overlapping with one at 08:00). This is a reasonable tradeoff because:
- It keeps the algorithm simple and fast — O(n) with a hash map.
- For most pet owners, tasks are scheduled at round times ("8am", "noon"), so exact-match detection catches the majority of real conflicts.
- Implementing full duration-overlap detection would add complexity without significant benefit for a daily pet care planner.

---

## 3. AI Collaboration

**a. How you used AI**

AI (Claude Code) was used throughout the project for:
- **Design brainstorming**: Drafting the UML class diagram and identifying relationships between Owner, Pet, Task, and Scheduler.
- **Code generation**: Scaffolding the dataclass skeletons and implementing sorting/filtering/conflict logic.
- **Test creation**: Generating a comprehensive pytest suite covering all core behaviors.
- **UI integration**: Wiring the Streamlit app to the backend logic with session state management.

The most helpful prompts were specific and contextual — referencing the existing code structure and asking for targeted implementations rather than open-ended generation.

**b. Judgment and verification**

The AI initially suggested a simpler Scheduler that only sorted by time. I extended it to sort by priority first (then time as tiebreaker) because a pet owner cares more about "what's most important" than strictly chronological order. I verified this by running the CLI demo and confirming that high-priority tasks appeared before low-priority ones even when scheduled later in the day.

---

## 4. Testing and Verification

**a. What you tested**

11 automated tests covering:
- **Task basics**: mark_complete changes status, adding tasks increases count, pet name tagging
- **Sorting**: chronological order by time, priority-based ordering
- **Filtering**: by pet name, by completion status
- **Conflict detection**: flags duplicate times, no false positives for different times
- **Recurrence**: daily tasks generate next occurrence, one-off tasks do not

These tests are important because they verify the core scheduling logic that users depend on — if sorting is wrong, the daily plan is useless; if recurrence breaks, owners miss recurring care.

**b. Confidence**

Confidence level: ⭐⭐⭐⭐ (4/5)

The core logic is well-tested. Edge cases I'd test next with more time:
- Tasks with invalid time formats (e.g., "25:00")
- Removing a pet and verifying its tasks are cleaned up
- Weekly recurrence date calculation across month boundaries
- Concurrent task completion (marking two tasks complete simultaneously)

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow worked extremely well. Building and verifying `main.py` before touching the Streamlit UI meant the backend logic was solid and tested before any UI complexity was added. The dataclass design kept the code clean and readable.

**b. What you would improve**

If I had another iteration, I would:
- Add duration-aware conflict detection (overlapping time ranges, not just exact matches)
- Implement data persistence (save/load to JSON) so tasks survive between app restarts
- Add a calendar view in the UI for weekly planning

**c. Key takeaway**

The most important lesson was that AI is most effective when you act as the architect — defining the structure and relationships first (UML), then using AI to implement within those guardrails. Without a clear design, AI-generated code can drift in unexpected directions. With a clear design, it accelerates implementation dramatically.
