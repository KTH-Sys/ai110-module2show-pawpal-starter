"""PawPal+ Streamlit UI — connected to the pawpal_system logic layer."""

import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# ---------- Session State Initialization ----------

if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

# ---------- Header ----------

st.title("🐾 PawPal+")
st.caption("Smart pet care scheduling — keep your furry friends happy and healthy.")

# ---------- Sidebar: Owner & Pet Management ----------

with st.sidebar:
    st.header("Owner")
    new_name = st.text_input("Owner name", value=owner.name)
    if new_name != owner.name:
        owner.name = new_name

    st.divider()
    st.header("Add a Pet")
    pet_name = st.text_input("Pet name", key="new_pet_name")
    species = st.selectbox("Species", ["dog", "cat", "bird", "rabbit", "other"])
    if st.button("Add Pet"):
        if pet_name.strip():
            owner.add_pet(Pet(name=pet_name.strip(), species=species))
            st.success(f"Added {pet_name}!")
        else:
            st.error("Please enter a pet name.")

    st.divider()
    st.header("Your Pets")
    if owner.pets:
        for pet in owner.pets:
            st.write(f"**{pet.name}** ({pet.species}) — {len(pet.tasks)} task(s)")
    else:
        st.info("No pets yet. Add one above.")

# ---------- Main Area: Add Tasks ----------

st.subheader("Schedule a Task")

if not owner.pets:
    st.info("Add a pet in the sidebar first.")
else:
    pet_options = [p.name for p in owner.pets]
    col1, col2 = st.columns(2)
    with col1:
        selected_pet = st.selectbox("For pet", pet_options)
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.text_input("Time (HH:MM)", value="08:00")
    with col2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["high", "medium", "low"])
        frequency = st.selectbox("Frequency", ["once", "daily", "weekly"])

    if st.button("Add Task"):
        pet = next(p for p in owner.pets if p.name == selected_pet)
        new_task = Task(
            title=task_title,
            time=task_time,
            duration_minutes=int(duration),
            priority=priority,
            frequency=frequency,
        )
        pet.add_task(new_task)
        st.success(f"Added '{task_title}' for {selected_pet} at {task_time}.")

# ---------- Daily Schedule ----------

st.divider()
st.subheader("Today's Schedule")

if st.button("Generate Schedule") or scheduler.get_all_tasks():
    all_tasks = scheduler.get_all_tasks()

    if not all_tasks:
        st.info("No tasks scheduled yet. Add some above!")
    else:
        # Conflict warnings
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for w in conflicts:
                st.warning(f"⚠️ {w}")

        # Show schedule sorted by priority then time
        schedule = scheduler.generate_schedule()
        if schedule:
            st.markdown("**Pending tasks** (sorted by priority → time):")
            table_data = []
            for t in schedule:
                priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(t.priority, "")
                table_data.append({
                    "Time": t.time,
                    "Task": t.title,
                    "Pet": t.pet_name,
                    "Duration": f"{t.duration_minutes} min",
                    "Priority": f"{priority_icon} {t.priority}",
                    "Frequency": t.frequency,
                })
            st.table(table_data)

        # Show completed tasks
        completed = scheduler.filter_by_status(completed=True)
        if completed:
            st.markdown("**Completed tasks:**")
            for t in completed:
                st.write(f"~~{t.time} — {t.title} ({t.pet_name})~~")

# ---------- Mark Complete ----------

st.divider()
st.subheader("Mark Task Complete")

pending = scheduler.filter_by_status(completed=False)
if pending:
    task_labels = {f"{t.time} — {t.title} ({t.pet_name})": t for t in pending}
    selected_label = st.selectbox("Select a task", list(task_labels.keys()))
    if st.button("Mark Complete"):
        task_to_complete = task_labels[selected_label]
        next_task = scheduler.mark_task_complete(task_to_complete)
        st.success(f"Marked '{task_to_complete.title}' as complete!")
        if next_task:
            st.info(f"Next {task_to_complete.frequency} occurrence created at {next_task.time}.")
        st.rerun()
else:
    st.info("No pending tasks to complete.")

# ---------- Filter by Pet ----------

st.divider()
st.subheader("Filter Tasks by Pet")

if owner.pets:
    filter_pet = st.selectbox("Choose a pet to filter", [p.name for p in owner.pets], key="filter_pet")
    filtered = scheduler.sort_by_time(scheduler.filter_by_pet(filter_pet))
    if filtered:
        for t in filtered:
            status = "✅" if t.completed else "⏳"
            st.write(f"{status} {t.time} — {t.title} ({t.priority}, {t.frequency})")
    else:
        st.info(f"No tasks for {filter_pet}.")
