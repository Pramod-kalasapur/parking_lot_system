"""Unit tests for the Parking Lot System."""

import time
import unittest

from parking_lot.grid import DistanceCalculator, GridMap
from parking_lot.manager import ParkingManager
from parking_lot.parser import CommandParser
from parking_lot.processor import CommandProcessor


SAMPLE_INPUT = """\
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park KA-01-HH-1234 White
park KA-01-HH-9999 White
park KA-01-BB-0001 Black
park KA-01-HH-7777 Red
park KA-01-HH-2701 Blue
park KA-01-HH-3141 Black
park KA-01-HH-5555 Grey
park KA-01-HH-6666 White
park KA-01-HH-8888 Red
park KA-01-HH-1111 Blue
leave 1 7
leave 2 1
status
park KA-01-P-333 White
park DL-12-AA-9999 White
park MH-04-AY-1111 Black
registration_numbers_for_cars_with_colour White
slot_numbers_for_cars_with_colour White
slot_number_for_registration_number KA-01-HH-3141
slot_number_for_registration_number MH-04-AY-1111
slot_number_for_registration_number TN-07-ZZ-0000
"""

EXPECTED_OUTPUT = """\
Created a parking lot with 10 usable slots
Allocated slot: (2, 1)
Allocated slot: (2, 3)
Allocated slot: (2, 5)
Allocated slot: (1, 7)
Allocated slot: (2, 7)
Allocated slot: (4, 7)
Allocated slot: (4, 4)
Allocated slot: (5, 7)
Allocated slot: (3, 1)
Allocated slot: (4, 2)
Slot (1, 7) is free
Slot (2, 1) is free
Slot Registration No Colour
(2, 3) KA-01-HH-9999 White
(2, 5) KA-01-BB-0001 Black
(2, 7) KA-01-HH-2701 Blue
(3, 1) KA-01-HH-8888 Red
(4, 2) KA-01-HH-1111 Blue
(4, 4) KA-01-HH-5555 Grey
(4, 7) KA-01-HH-3141 Black
(5, 7) KA-01-HH-6666 White
Allocated slot: (2, 1)
Allocated slot: (1, 7)
Sorry, parking lot is full
DL-12-AA-9999, KA-01-P-333, KA-01-HH-9999, KA-01-HH-6666
(1, 7), (2, 1), (2, 3), (5, 7)
(4, 7)
Not found
Not found
"""


def run_text(input_text: str) -> str:
    processor = CommandProcessor()
    output_lines = []
    for command in CommandParser.parse_stream(iter(input_text.splitlines())):
        output_lines.extend(processor.process(command))
    return "\n".join(output_lines) + ("\n" if output_lines else "")


def usable_slots(rows: int, cols: int, lines: list[str]):
    grid = GridMap.from_lines(rows, cols, lines)
    return DistanceCalculator.calculate_usable_slots(grid)


class ParkingLotEndToEndTests(unittest.TestCase):
    def test_golden_output_matches_exactly(self) -> None:
        self.assertEqual(run_text(SAMPLE_INPUT), EXPECTED_OUTPUT)

    def test_full_lot_then_leave_reuses_that_slot(self) -> None:
        output = run_text(
            """\
create_parking_lot 1 2
EP
park A White
park B Black
leave 1 2
park B Black
"""
        )

        self.assertEqual(
            output,
            "Created a parking lot with 1 usable slots\n"
            "Allocated slot: (1, 2)\n"
            "Sorry, parking lot is full\n"
            "Slot (1, 2) is free\n"
            "Allocated slot: (1, 2)\n",
        )

    def test_leave_then_park_uses_nearest_free_slot(self) -> None:
        output = run_text(
            """\
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park A White
park B White
park C White
leave 2 1
leave 2 5
park D White
"""
        )

        self.assertTrue(output.endswith("Allocated slot: (2, 1)\n"))

    def test_status_order_is_by_slot_not_allocation_order(self) -> None:
        output = run_text(
            """\
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park A White
park B Black
park C Red
leave 2 1
park D Blue
status
"""
        )

        status_lines = output.splitlines()[-4:]
        self.assertEqual(
            status_lines,
            [
                "Slot Registration No Colour",
                "(2, 1) D Blue",
                "(2, 3) B Black",
                "(2, 5) C Red",
            ],
        )

    def test_colour_lookup_is_case_insensitive_and_ordered_by_slot(self) -> None:
        output = run_text(
            """\
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park A White
park B white
park C BLACK
registration_numbers_for_cars_with_colour WHITE
slot_numbers_for_cars_with_colour white
"""
        )

        self.assertEqual(output.splitlines()[-2:], ["A, B", "(2, 1), (2, 3)"])

    def test_registration_lookup_is_case_insensitive(self) -> None:
        output = run_text(
            """\
create_parking_lot 1 2
EP
park Ka-01 White
slot_number_for_registration_number ka-01
slot_number_for_registration_number missing
"""
        )

        self.assertEqual(output.splitlines()[-2:], ["(1, 2)", "Not found"])

    def test_empty_lot_status(self) -> None:
        output = run_text(
            """\
create_parking_lot 1 2
EP
status
"""
        )

        self.assertEqual(output.splitlines()[-1], "Parking lot is empty")

    def test_invalid_inputs_do_not_crash(self) -> None:
        output = run_text(
            """\
park A White
bad_command
create_parking_lot x 2
create_parking_lot 1 2
EP
park A White Extra
park A White
park a Black
leave x 2
leave 1 1
leave 1 2
leave 1 2
status extra
"""
        )

        self.assertEqual(
            output.splitlines(),
            [
                "Parking lot not created",
                "Invalid command",
                "Invalid command",
                "Created a parking lot with 1 usable slots",
                "Invalid command",
                "Allocated slot: (1, 2)",
                "Car already parked",
                "Invalid command",
                "Invalid slot",
                "Slot (1, 2) is free",
                "Slot (1, 2) is already free",
                "Invalid command",
            ],
        )

    def test_zero_usable_slots(self) -> None:
        output = run_text(
            """\
create_parking_lot 3 3
E##
#P#
###
park A White
"""
        )

        self.assertEqual(
            output,
            "Created a parking lot with 0 usable slots\n"
            "Sorry, parking lot is full\n",
        )


class DistanceCalculatorTests(unittest.TestCase):
    def test_sample_distances_and_unreachable_slots(self) -> None:
        slots = sorted(
            usable_slots(
                5,
                7,
                [
                    "E.....P",
                    "P#P#P.P",
                    "P.....#",
                    "PP#P#.P",
                    "P####.P",
                ],
            )
        )

        actual = [(slot.distance, slot.row, slot.col) for slot in slots]
        self.assertEqual(
            actual,
            [
                (1, 2, 1),
                (3, 2, 3),
                (5, 2, 5),
                (6, 1, 7),
                (7, 2, 7),
                (9, 4, 7),
                (10, 4, 4),
                (10, 5, 7),
                (12, 3, 1),
                (12, 4, 2),
            ],
        )

    def test_walls_block_unreachable_near_slot(self) -> None:
        slots = usable_slots(3, 4, ["E##.", "##P.", "...."])

        self.assertEqual(slots, [])

    def test_tie_break_prefers_smaller_row_then_column(self) -> None:
        manager = ParkingManager(usable_slots(3, 3, [".P.", "PEP", "..."]))

        self.assertEqual(manager.park("A", "White")[2], (1, 2))
        self.assertEqual(manager.park("B", "White")[2], (2, 1))
        self.assertEqual(manager.park("C", "White")[2], (2, 3))

    def test_slot_touching_two_roads_uses_smaller_distance(self) -> None:
        slots = usable_slots(3, 3, ["E..", ".#P", "..."])

        self.assertEqual([(s.distance, s.row, s.col) for s in slots], [(3, 2, 3)])

    def test_slot_adjacent_directly_to_entrance_has_distance_one(self) -> None:
        slots = usable_slots(1, 2, ["EP"])

        self.assertEqual([(s.distance, s.row, s.col) for s in slots], [(1, 1, 2)])

    def test_cars_do_not_path_through_parking_cells(self) -> None:
        slots = usable_slots(1, 4, ["EP.P"])

        self.assertEqual([(s.distance, s.row, s.col) for s in slots], [(1, 1, 2)])


class PerformanceTests(unittest.TestCase):
    def test_large_grid_and_many_commands_finish_quickly(self) -> None:
        rows = 1000
        cols = 1000
        grid_lines = ["E" + "." * (cols - 2) + "P"] + ["." * cols for _ in range(rows - 1)]

        start = time.perf_counter()
        slots = usable_slots(rows, cols, grid_lines)
        manager = ParkingManager(slots)

        for i in range(50_000):
            manager.park(f"CAR-{i}", "White")
            manager.leave(1, cols)

        elapsed = time.perf_counter() - start
        self.assertEqual(manager.usable_count, 1)
        self.assertLess(elapsed, 20.0, f"performance test took {elapsed:.3f}s")


if __name__ == "__main__":
    unittest.main()
