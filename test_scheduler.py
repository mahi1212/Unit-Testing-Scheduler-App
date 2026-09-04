"""Unit tests for the Intelligent Timetable Scheduler."""

import unittest

from scheduler import Course, IntelligentTimetableScheduler, Lecturer, Room


class TestIntelligentTimetableScheduler(unittest.TestCase):
    """Test suite covering SB01–SB10 from the requirements specification."""

    def setUp(self):
        self.scheduler = IntelligentTimetableScheduler()

    def test_normal_behavior_successful_schedule(self):
        """SB01: Successfully schedule independent courses."""
        rooms = [Room("R1", 30), Room("R2", 50)]
        lecturers = [
            Lecturer("L1", ["Mon 09:00", "Mon 11:00"]),
            Lecturer("L2", ["Tue 09:00", "Tue 11:00"]),
        ]
        courses = [
            Course("C1", "L1", 20),
            Course("C2", "L2", 40),
        ]
        time_slots = ["Mon 09:00", "Mon 11:00", "Tue 09:00", "Tue 11:00"]

        result = self.scheduler.schedule(courses, rooms, lecturers, time_slots)

        self.assertEqual(len(result), 2)
        self.assertIn("C1", result)
        self.assertIn("C2", result)
        for course_id, entry in result.items():
            self.assertIn("room_id", entry)
            self.assertIn("time_slot", entry)
            self.assertIn("slot_index", entry)

    def test_room_capacity_constraint(self):
        """SB02 & SB03: Room capacity enforcement and overflow rejection."""
        rooms = [Room("R1", 15), Room("R2", 40)]
        lecturer = Lecturer("L1", ["Mon 09:00", "Mon 11:00"])
        courses = [Course("C1", "L1", 30)]
        time_slots = ["Mon 09:00", "Mon 11:00"]

        result = self.scheduler.schedule(courses, [rooms[1]], [lecturer], time_slots)
        self.assertEqual(result["C1"]["room_id"], "R2")

        oversized = Course("C2", "L1", 50)
        with self.assertRaises(ValueError):
            self.scheduler.schedule([oversized], rooms, [lecturer], time_slots)

    def test_lecturer_availability_constraint(self):
        """SB04: Courses scheduled only within lecturer availability."""
        rooms = [Room("R1", 50)]
        lecturer = Lecturer("L1", ["Fri 09:00"])
        courses = [Course("C1", "L1", 20)]
        time_slots = ["Mon 09:00", "Wed 09:00", "Fri 09:00"]

        result = self.scheduler.schedule(courses, rooms, [lecturer], time_slots)

        self.assertEqual(result["C1"]["time_slot"], "Fri 09:00")

    def test_room_clash_prevention(self):
        """SB05: Reject scheduling when room double-booking is unavoidable."""
        rooms = [Room("R1", 50)]
        lecturers = [
            Lecturer("L1", ["Mon 09:00"]),
            Lecturer("L2", ["Mon 09:00"]),
        ]
        courses = [
            Course("C1", "L1", 20),
            Course("C2", "L2", 25),
        ]
        time_slots = ["Mon 09:00"]

        with self.assertRaises(ValueError):
            self.scheduler.schedule(courses, rooms, lecturers, time_slots)

    def test_lecturer_clash_prevention(self):
        """SB06: Reject scheduling when lecturer double-booking is unavoidable."""
        rooms = [Room("R1", 50), Room("R2", 50)]
        lecturer = Lecturer("L1", ["Mon 09:00"])
        courses = [
            Course("C1", "L1", 20),
            Course("C2", "L1", 25),
        ]
        time_slots = ["Mon 09:00", "Mon 11:00"]

        with self.assertRaises(ValueError):
            self.scheduler.schedule(courses, rooms, [lecturer], time_slots)

    def test_preferred_time_slots_prioritization(self):
        """SB07: Preferred slots are chosen over general availability."""
        rooms = [Room("R1", 50)]
        lecturer = Lecturer(
            "L1",
            ["Mon 09:00", "Mon 11:00"],
            preferred_slots=["Mon 11:00"],
        )
        courses = [Course("C1", "L1", 20)]
        time_slots = ["Mon 09:00", "Mon 11:00"]

        result = self.scheduler.schedule(courses, rooms, [lecturer], time_slots)

        self.assertEqual(result["C1"]["time_slot"], "Mon 11:00")

    def test_prerequisite_ordering_constraint(self):
        """SB08: Prerequisite courses must be scheduled before dependents."""
        rooms = [Room("R1", 50)]
        lecturer = Lecturer("L1", ["Mon 09:00", "Mon 11:00", "Mon 13:00"])
        courses = [
            Course("C1", "L1", 20),
            Course("C2", "L1", 20, prerequisites=["C1"]),
        ]
        time_slots = ["Mon 09:00", "Mon 11:00", "Mon 13:00"]

        result = self.scheduler.schedule(courses, rooms, [lecturer], time_slots)

        self.assertLess(
            result["C1"]["slot_index"],
            result["C2"]["slot_index"],
        )

    def test_circular_prerequisite_detection(self):
        """SB09: Circular prerequisite loops are rejected immediately."""
        rooms = [Room("R1", 50)]
        lecturer = Lecturer("L1", ["Mon 09:00", "Mon 11:00"])
        courses = [
            Course("C1", "L1", 20, prerequisites=["C2"]),
            Course("C2", "L1", 20, prerequisites=["C1"]),
        ]
        time_slots = ["Mon 09:00", "Mon 11:00"]

        with self.assertRaises(ValueError):
            self.scheduler.schedule(courses, rooms, [lecturer], time_slots)

    def test_invalid_input_scenarios(self):
        """SB10: Invalid model data raises ValueError at construction."""
        with self.assertRaises(ValueError):
            Room("R1", 0)

        with self.assertRaises(ValueError):
            Room("R1", -5)

        with self.assertRaises(ValueError):
            Course("C1", "L1", -10)

        with self.assertRaises(ValueError):
            Lecturer("L1", ["Mon 09:00"], preferred_slots=["Tue 09:00"])

    def test_empty_time_slots_validation(self):
        """SB10: Empty time slot list is rejected before scheduling."""
        rooms = [Room("R1", 50)]
        lecturer = Lecturer("L1", ["Mon 09:00"])
        courses = [Course("C1", "L1", 20)]

        with self.assertRaises(ValueError):
            self.scheduler.schedule(courses, rooms, [lecturer], [])


if __name__ == "__main__":
    unittest.main()
