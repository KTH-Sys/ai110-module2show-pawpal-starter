"""PawPal+ Logic Layer — Owner, Pet, Task, and Scheduler classes."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
import uuid


@dataclass
class Task:
    """A single pet care activity."""

    title: str
    time: str  # "HH:MM" format
    duration_minutes: int
    priority: str = "medium"  # "low", "medium", "high"
    frequency: str = "once"  # "once", "daily", "weekly"
    completed: bool = False
    pet_name: str = ""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def __str__(self):
        status = "Done" if self.completed else "Pending"
        return (
            f"[{status}] {self.time} - {self.title} "
            f"({self.duration_minutes}min, {self.priority} priority, {self.frequency})"
        )


@dataclass
class Pet:
    """A pet with a name, species, and list of care tasks."""

    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task and tag it with this pet's name."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task_id: str):
        """Remove a task by its id."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def __str__(self):
        return f"{self.name} ({self.species}) — {len(self.tasks)} task(s)"


@dataclass
class Owner:
    """A pet owner who manages multiple pets."""

    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet):
        """Register a new pet."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list:
        """Collect every task across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def __str__(self):
        pet_names = ", ".join(p.name for p in self.pets) or "none"
        return f"Owner {self.name} — pets: {pet_names}"


class Scheduler:
    """The scheduling brain — sorts, filters, detects conflicts, and handles recurrence."""

    PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}

    def __init__(self, owner: Owner):
        self.owner = owner

    # ------ retrieval ------

    def get_all_tasks(self) -> list:
        """Return every task from the owner's pets."""
        return self.owner.get_all_tasks()

    # ------ sorting ------

    def sort_by_time(self, tasks: list = None) -> list:
        """Return tasks sorted chronologically by their HH:MM time string."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(tasks, key=lambda t: t.time)

    def sort_by_priority(self, tasks: list = None) -> list:
        """Return tasks sorted by priority (high first), then by time."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return sorted(
            tasks,
            key=lambda t: (self.PRIORITY_ORDER.get(t.priority, 1), t.time),
        )

    # ------ filtering ------

    def filter_by_pet(self, pet_name: str, tasks: list = None) -> list:
        """Return only the tasks belonging to a specific pet."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.pet_name == pet_name]

    def filter_by_status(self, completed: bool, tasks: list = None) -> list:
        """Return tasks filtered by completion status."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        return [t for t in tasks if t.completed == completed]

    # ------ conflict detection ------

    def detect_conflicts(self, tasks: list = None) -> list:
        """Return warning strings for any tasks scheduled at the same time."""
        tasks = tasks if tasks is not None else self.get_all_tasks()
        time_map: dict = {}
        for task in tasks:
            time_map.setdefault(task.time, []).append(task)

        warnings = []
        for time_slot, group in time_map.items():
            if len(group) > 1:
                names = ", ".join(f"'{t.title}' ({t.pet_name})" for t in group)
                warnings.append(
                    f"Conflict at {time_slot}: {names}"
                )
        return warnings

    # ------ recurring tasks ------

    def generate_next_occurrence(self, task: Task) -> Task | None:
        """Create the next occurrence of a recurring task. Returns None for one-off tasks."""
        if task.frequency == "once":
            return None

        today = datetime.now()
        delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
        next_date = today + delta

        new_task = Task(
            title=task.title,
            time=task.time,
            duration_minutes=task.duration_minutes,
            priority=task.priority,
            frequency=task.frequency,
            completed=False,
            pet_name=task.pet_name,
        )
        return new_task

    def mark_task_complete(self, task: Task) -> Task | None:
        """Mark a task complete and auto-create the next occurrence if recurring."""
        task.mark_complete()
        next_task = self.generate_next_occurrence(task)
        if next_task is not None:
            # Add the new task to the correct pet
            for pet in self.owner.pets:
                if pet.name == task.pet_name:
                    pet.add_task(next_task)
                    break
        return next_task

    # ------ schedule generation ------

    def generate_schedule(self) -> list:
        """Return today's pending tasks sorted by priority then time."""
        pending = self.filter_by_status(completed=False)
        return self.sort_by_priority(pending)

    def print_schedule(self):
        """Print a formatted daily schedule to the terminal."""
        schedule = self.generate_schedule()
        conflicts = self.detect_conflicts(schedule)

        print(f"\n{'='*50}")
        print(f"  Daily Schedule for {self.owner.name}")
        print(f"{'='*50}")

        if conflicts:
            print("\n  ** WARNINGS **")
            for w in conflicts:
                print(f"  - {w}")

        if not schedule:
            print("\n  No pending tasks for today.")
        else:
            current_pet = None
            for task in schedule:
                if task.pet_name != current_pet:
                    current_pet = task.pet_name
                print(f"  {task}")

        print(f"{'='*50}\n")
