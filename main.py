"""PawPal+ CLI Demo — verifies backend logic before connecting to Streamlit."""

from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # --- Create owner and pets ---
    owner = Owner(name="Jordan")

    mochi = Pet(name="Mochi", species="dog")
    whiskers = Pet(name="Whiskers", species="cat")

    owner.add_pet(mochi)
    owner.add_pet(whiskers)

    # --- Add tasks (intentionally out of order) ---
    mochi.add_task(Task(title="Morning walk", time="07:30", duration_minutes=30, priority="high", frequency="daily"))
    mochi.add_task(Task(title="Breakfast", time="08:00", duration_minutes=10, priority="high", frequency="daily"))
    mochi.add_task(Task(title="Flea medication", time="09:00", duration_minutes=5, priority="medium", frequency="weekly"))
    mochi.add_task(Task(title="Evening walk", time="17:00", duration_minutes=30, priority="high", frequency="daily"))

    whiskers.add_task(Task(title="Breakfast", time="08:00", duration_minutes=5, priority="high", frequency="daily"))
    whiskers.add_task(Task(title="Litter box clean", time="09:00", duration_minutes=10, priority="medium", frequency="daily"))
    whiskers.add_task(Task(title="Playtime", time="15:00", duration_minutes=20, priority="low", frequency="daily"))

    scheduler = Scheduler(owner)

    # --- Print the full schedule ---
    scheduler.print_schedule()

    # --- Demonstrate sorting by time ---
    print("Tasks sorted by time:")
    for t in scheduler.sort_by_time():
        print(f"  {t}")

    # --- Demonstrate filtering ---
    print("\nMochi's tasks only:")
    for t in scheduler.filter_by_pet("Mochi"):
        print(f"  {t}")

    # --- Demonstrate conflict detection ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("\nConflict warnings:")
        for w in conflicts:
            print(f"  ⚠ {w}")

    # --- Demonstrate recurring task completion ---
    print("\nMarking Mochi's morning walk as complete...")
    morning_walk = mochi.tasks[0]
    next_task = scheduler.mark_task_complete(morning_walk)
    if next_task:
        print(f"  Next occurrence created: {next_task}")
    print(f"  Original task status: {morning_walk}")

    # --- Print updated schedule ---
    scheduler.print_schedule()


if __name__ == "__main__":
    main()
