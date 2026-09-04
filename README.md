# Intelligent Timetable Scheduler

Constraint-based university timetable generator built for **PRT582 — Software Engineering: Process and Tools** (CDU).

## Features

The scheduler assigns courses to rooms and time slots while enforcing:

- **Room capacity** — enrollment must not exceed room capacity
- **Lecturer availability** — courses only in available windows
- **No room clashes** — one course per room per slot
- **No lecturer clashes** — one course per lecturer per slot
- **Preferred time slots** — preferred slots tried first, with fallback
- **Prerequisite ordering** — prerequisites scheduled before dependents
- **Circular dependency detection** — invalid prerequisite loops rejected early

## Project Structure

```
scheduler.py        # Domain models and backtracking scheduler
test_scheduler.py   # Unit test suite (10 tests, SB01–SB10)
requirements.txt    # No external dependencies
```

## Requirements

- Python 3.10 or later

## Running Tests

```bash
python3 -m unittest test_scheduler.py -v
```

### Code Coverage (Section 6.2)

```bash
pip install -r requirements.txt
coverage run -m unittest test_scheduler.py
coverage report
coverage html   # optional: generates htmlcov/index.html
```

All **15 tests** should pass:

| Test | Requirement |
|------|-------------|
| `test_normal_behavior_successful_schedule` | SB01 |
| `test_room_capacity_constraint` | SB02 & SB03 |
| `test_lecturer_availability_constraint` | SB04 |
| `test_room_clash_prevention` | SB05 |
| `test_lecturer_clash_prevention` | SB06 |
| `test_preferred_time_slots_prioritization` | SB07 |
| `test_prerequisite_ordering_constraint` | SB08 |
| `test_circular_prerequisite_detection` | SB09 |
| `test_invalid_input_scenarios` | SB10 |
| `test_empty_time_slots_validation` | SB10 |
| `test_nfr1_execution_efficiency` | NFR1 |
| `test_nfr3_deterministic_search` | NFR3 |
| `test_missing_prerequisite_course_rejected` | Edge case |
| `test_lecturer_clash_skipped_during_search` | Backtracking |
| `test_topological_sort_detects_cycles` | Secondary cycle guard |

## Usage Example

```python
from scheduler import Course, IntelligentTimetableScheduler, Lecturer, Room

scheduler = IntelligentTimetableScheduler()

rooms = [Room("R101", 40), Room("R102", 60)]
lecturers = [
    Lecturer("L1", ["Mon 09:00", "Mon 11:00"], preferred_slots=["Mon 09:00"]),
    Lecturer("L2", ["Tue 09:00"]),
]
courses = [
    Course("CS101", "L1", 35),
    Course("CS102", "L2", 50, prerequisites=["CS101"]),
]
time_slots = ["Mon 09:00", "Mon 11:00", "Tue 09:00"]

timetable = scheduler.schedule(courses, rooms, lecturers, time_slots)
print(timetable)
```

## Author

Mahinur Rahman — s398451
