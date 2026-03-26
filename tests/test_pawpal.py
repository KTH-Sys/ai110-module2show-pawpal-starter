"""Automated tests for the PawPal+ scheduling system."""

from pawpal_system import Owner, Pet, Task, Scheduler


# ---------- Task basics ----------

def test_task_mark_complete():
    """Marking a task complete changes its status."""
    task = Task(title="Walk", time="07:00", duration_minutes=30)
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_count():
    """Adding a task to a pet increases the pet's task count."""
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(title="Walk", time="07:00", duration_minutes=30))
    assert len(pet.tasks) == 1
    pet.add_task(Task(title="Feed", time="08:00", duration_minutes=10))
    assert len(pet.tasks) == 2


def test_task_pet_name_tagged():
    """Adding a task to a pet tags it with the pet's name."""
    pet = Pet(name="Whiskers", species="cat")
    task = Task(title="Feed", time="08:00", duration_minutes=5)
    pet.add_task(task)
    assert task.pet_name == "Whiskers"


# ---------- Sorting ----------

def test_sort_by_time():
    """Tasks are returned in chronological order."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Evening walk", time="17:00", duration_minutes=30))
    pet.add_task(Task(title="Morning walk", time="07:00", duration_minutes=30))
    pet.add_task(Task(title="Lunch feed", time="12:00", duration_minutes=10))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_time()

    times = [t.time for t in sorted_tasks]
    assert times == ["07:00", "12:00", "17:00"]


def test_sort_by_priority():
    """Tasks are sorted high → medium → low, then by time within each level."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Play", time="10:00", duration_minutes=20, priority="low"))
    pet.add_task(Task(title="Meds", time="09:00", duration_minutes=5, priority="high"))
    pet.add_task(Task(title="Groom", time="11:00", duration_minutes=15, priority="medium"))

    scheduler = Scheduler(owner)
    sorted_tasks = scheduler.sort_by_priority()
    priorities = [t.priority for t in sorted_tasks]
    assert priorities == ["high", "medium", "low"]


# ---------- Filtering ----------

def test_filter_by_pet():
    """Filtering returns only the specified pet's tasks."""
    owner = Owner(name="Test")
    dog = Pet(name="Rex", species="dog")
    cat = Pet(name="Luna", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)
    dog.add_task(Task(title="Walk", time="07:00", duration_minutes=30))
    cat.add_task(Task(title="Feed", time="08:00", duration_minutes=5))

    scheduler = Scheduler(owner)
    rex_tasks = scheduler.filter_by_pet("Rex")
    assert len(rex_tasks) == 1
    assert rex_tasks[0].title == "Walk"


def test_filter_by_status():
    """Filtering by completed status works correctly."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    t1 = Task(title="Walk", time="07:00", duration_minutes=30)
    t2 = Task(title="Feed", time="08:00", duration_minutes=10)
    pet.add_task(t1)
    pet.add_task(t2)
    t1.mark_complete()

    scheduler = Scheduler(owner)
    assert len(scheduler.filter_by_status(completed=True)) == 1
    assert len(scheduler.filter_by_status(completed=False)) == 1


# ---------- Conflict detection ----------

def test_detect_conflicts():
    """Two tasks at the same time produce a conflict warning."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Walk", time="08:00", duration_minutes=30))
    pet.add_task(Task(title="Feed", time="08:00", duration_minutes=10))

    scheduler = Scheduler(owner)
    warnings = scheduler.detect_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]


def test_no_conflicts_when_different_times():
    """No warnings when tasks are at different times."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    pet.add_task(Task(title="Walk", time="07:00", duration_minutes=30))
    pet.add_task(Task(title="Feed", time="08:00", duration_minutes=10))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


# ---------- Recurring tasks ----------

def test_daily_recurrence():
    """Marking a daily task complete creates a new pending task for the same pet."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    task = Task(title="Walk", time="07:00", duration_minutes=30, frequency="daily")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    assert len(pet.tasks) == 1

    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is not None
    assert next_task.completed is False
    assert next_task.frequency == "daily"
    assert len(pet.tasks) == 2  # original + new occurrence


def test_one_off_task_no_recurrence():
    """A one-off task does not generate a next occurrence."""
    owner = Owner(name="Test")
    pet = Pet(name="Buddy", species="dog")
    owner.add_pet(pet)
    task = Task(title="Vet visit", time="10:00", duration_minutes=60, frequency="once")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    next_task = scheduler.mark_task_complete(task)

    assert task.completed is True
    assert next_task is None
    assert len(pet.tasks) == 1
