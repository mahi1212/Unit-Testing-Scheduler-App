"""Intelligent Timetable Scheduler — constraint-based course scheduling."""


class Room:
    """Physical classroom with a fixed seat capacity."""

    def __init__(self, room_id: str, capacity: int):
        if capacity <= 0:
            raise ValueError("Room capacity must be positive")
        self.room_id = room_id
        self.capacity = capacity


class Lecturer:
    """Instructor with availability windows and optional preferred slots."""

    def __init__(
        self,
        lecturer_id: str,
        availability: list[str],
        preferred_slots: list[str] | None = None,
    ):
        preferred_slots = preferred_slots or []
        for slot in preferred_slots:
            if slot not in availability:
                raise ValueError(
                    f"Preferred slot '{slot}' is not in lecturer availability"
                )
        self.lecturer_id = lecturer_id
        self.availability = availability
        self.preferred_slots = preferred_slots


class Course:
    """Academic course assigned to a lecturer with optional prerequisites."""

    def __init__(
        self,
        course_id: str,
        lecturer_id: str,
        enrolled_students: int,
        prerequisites: list[str] | None = None,
    ):
        if enrolled_students < 0:
            raise ValueError("Enrolled students cannot be negative")
        self.course_id = course_id
        self.lecturer_id = lecturer_id
        self.enrolled_students = enrolled_students
        self.prerequisites = prerequisites or []


class IntelligentTimetableScheduler:
    """Backtracking scheduler satisfying room, lecturer, and prerequisite constraints."""

    def schedule(
        self,
        courses: list[Course],
        rooms: list[Room],
        lecturers: list[Lecturer],
        time_slots: list[str],
    ) -> dict[str, dict]:
        if not time_slots:
            raise ValueError("Time slots cannot be empty")

        self._check_circular_dependencies(courses)

        lecturer_map = {lecturer.lecturer_id: lecturer for lecturer in lecturers}

        for course in courses:
            if not any(room.capacity >= course.enrolled_students for room in rooms):
                raise ValueError(
                    f"No room with sufficient capacity for course {course.course_id}"
                )

        course_map = {course.course_id: course for course in courses}
        sorted_courses = self._topological_sort(courses)
        result = self._backtrack(
            sorted_courses,
            rooms,
            lecturer_map,
            course_map,
            time_slots,
            {},
            0,
        )
        if result is None:
            raise ValueError("No valid schedule exists")
        return result

    def _check_circular_dependencies(self, courses: list[Course]) -> None:
        adjacency = {course.course_id: course.prerequisites for course in courses}
        visited: dict[str, str] = {}

        def dfs(node: str) -> None:
            if node in visited:
                if visited[node] == "visiting":
                    raise ValueError("Circular dependency detected")
                return
            visited[node] = "visiting"
            for neighbor in adjacency.get(node, []):
                dfs(neighbor)
            visited[node] = "visited"

        for course in courses:
            dfs(course.course_id)

    def _topological_sort(self, courses: list[Course]) -> list[Course]:
        course_map = {course.course_id: course for course in courses}
        in_degree = {course.course_id: 0 for course in courses}
        for course in courses:
            for prereq in course.prerequisites:
                if prereq in in_degree:
                    in_degree[course.course_id] += 1

        queue = [cid for cid, degree in in_degree.items() if degree == 0]
        sorted_ids: list[str] = []
        while queue:
            queue.sort()
            current = queue.pop(0)
            sorted_ids.append(current)
            for course in courses:
                if current in course.prerequisites:
                    in_degree[course.course_id] -= 1
                    if in_degree[course.course_id] == 0:
                        queue.append(course.course_id)

        if len(sorted_ids) != len(courses):
            raise ValueError("Circular dependency detected")
        return [course_map[course_id] for course_id in sorted_ids]

    def _candidate_slots(
        self, lecturer: Lecturer, time_slots: list[str]
    ) -> list[tuple[int, str]]:
        available = [
            (index, slot)
            for index, slot in enumerate(time_slots)
            if slot in lecturer.availability
        ]
        preferred = [
            (index, slot)
            for index, slot in available
            if slot in lecturer.preferred_slots
        ]
        non_preferred = [
            (index, slot)
            for index, slot in available
            if slot not in lecturer.preferred_slots
        ]
        return preferred + non_preferred

    def _backtrack(
        self,
        courses: list[Course],
        rooms: list[Room],
        lecturer_map: dict[str, Lecturer],
        course_map: dict[str, Course],
        time_slots: list[str],
        assignment: dict[str, dict],
        course_index: int,
    ) -> dict[str, dict] | None:
        if course_index == len(courses):
            return assignment

        course = courses[course_index]
        lecturer = lecturer_map[course.lecturer_id]
        candidate_slots = self._candidate_slots(lecturer, time_slots)
        suitable_rooms = [
            room
            for room in rooms
            if room.capacity >= course.enrolled_students
        ]

        for slot_index, slot in candidate_slots:
            if not self._prerequisites_satisfied(course, slot_index, assignment):
                continue

            for room in suitable_rooms:
                if self._has_room_clash(room.room_id, slot_index, assignment):
                    continue
                if self._has_lecturer_clash(
                    course.lecturer_id, slot_index, assignment, course_map
                ):
                    continue

                assignment[course.course_id] = {
                    "room_id": room.room_id,
                    "time_slot": slot,
                    "slot_index": slot_index,
                }
                result = self._backtrack(
                    courses,
                    rooms,
                    lecturer_map,
                    course_map,
                    time_slots,
                    assignment,
                    course_index + 1,
                )
                if result is not None:
                    return result
                del assignment[course.course_id]

        return None

    def _prerequisites_satisfied(
        self,
        course: Course,
        slot_index: int,
        assignment: dict[str, dict],
    ) -> bool:
        for prereq_id in course.prerequisites:
            if prereq_id not in assignment:
                return False
            if assignment[prereq_id]["slot_index"] >= slot_index:
                return False
        return True

    def _has_room_clash(
        self, room_id: str, slot_index: int, assignment: dict[str, dict]
    ) -> bool:
        return any(
            entry["room_id"] == room_id and entry["slot_index"] == slot_index
            for entry in assignment.values()
        )

    def _has_lecturer_clash(
        self,
        lecturer_id: str,
        slot_index: int,
        assignment: dict[str, dict],
        course_map: dict[str, Course],
    ) -> bool:
        for course_id, entry in assignment.items():
            if entry["slot_index"] == slot_index:
                if course_map[course_id].lecturer_id == lecturer_id:
                    return True
        return False
