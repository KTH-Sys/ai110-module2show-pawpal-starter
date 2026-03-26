# PawPal+ 🐾

A smart pet care management system that helps owners keep their furry friends happy and healthy. PawPal+ tracks daily routines — feedings, walks, medications, and appointments — while using algorithmic logic to organize and prioritize tasks.

## Features

- **Multi-pet management**: Add and manage multiple pets with different species
- **Task scheduling**: Create tasks with time, duration, priority (high/medium/low), and frequency (once/daily/weekly)
- **Priority-based scheduling**: Tasks sorted by priority first, then chronologically — so urgent care always comes first
- **Conflict detection**: Automatic warnings when two tasks are scheduled at the same time
- **Recurring task automation**: Daily and weekly tasks auto-regenerate after completion
- **Filtering**: View tasks by pet or by completion status
- **Streamlit UI**: Interactive web interface with color-coded priorities and real-time schedule generation

## Smarter Scheduling

PawPal+ goes beyond simple list management with built-in algorithmic intelligence:

- **Sorting by priority → time**: High-priority tasks (medications, walks) surface first, with chronological ordering as a tiebreaker
- **Conflict warnings**: A hash-map based detector flags duplicate time slots in O(n) time
- **Daily recurrence**: Completing a recurring task auto-creates the next occurrence, so owners never forget routine care
- **Smart filtering**: Instantly slice the schedule by pet name or completion status

## Getting Started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run the CLI Demo

```bash
python main.py
```

### Run the Streamlit App

```bash
streamlit run app.py
```

## Project Structure

| File | Purpose |
|---|---|
| `pawpal_system.py` | Core logic layer — Owner, Pet, Task, Scheduler classes |
| `main.py` | CLI demo script for verifying backend logic |
| `app.py` | Streamlit UI connected to the logic layer |
| `tests/test_pawpal.py` | Automated pytest suite (11 tests) |
| `reflection.md` | Design decisions, tradeoffs, and AI collaboration notes |

## Testing PawPal+

Run the full test suite:

```bash
python -m pytest tests/ -v
```

The test suite covers:
- Task completion and state changes
- Adding/tagging tasks to pets
- Chronological and priority-based sorting
- Filtering by pet name and completion status
- Conflict detection (true positives and no false positives)
- Recurring task generation (daily tasks) and one-off task behavior

**Confidence Level**: ⭐⭐⭐⭐ (4/5) — Core scheduling logic is thoroughly tested. Edge cases like invalid time formats and cross-month recurrence would benefit from additional coverage.

## Architecture

The system follows a layered design:

- **Data layer**: `Task` and `Pet` dataclasses hold state
- **Domain layer**: `Owner` aggregates pets; `Scheduler` implements all algorithmic logic
- **Presentation layer**: `app.py` (Streamlit) and `main.py` (CLI) consume the domain layer

The Scheduler retrieves tasks through the Owner → Pet chain, keeping the data flow unidirectional and testable.
