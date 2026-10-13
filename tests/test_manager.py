"""Unit tests for ParkingManager."""

import unittest

from parking_lot.constants import (
    MSG_CAR_ALREADY_PARKED,
    MSG_INVALID_SLOT,
    MSG_LOT_EMPTY,
    MSG_LOT_FULL,
    MSG_NOT_FOUND,
    MSG_SLOT_ALREADY_FREE,
)
from parking_lot.manager import ParkingManager
from parking_lot.models import Slot, SlotDistance


class TestParkingManager(unittest.TestCase):
    """Verifies allocation, deallocation, lookups, and state invariants."""

    def setUp(self):
        # 3 usable slots: S1=(1, 2) dist 2, S2=(3, 1) dist 5, S3=(2, 4) dist 5
        self.slots = [
            SlotDistance(distance=2, row=1, col=2),
            SlotDistance(distance=5, row=3, col=1),
            SlotDistance(distance=5, row=2, col=4),
        ]
        self.manager = ParkingManager(self.slots)

    def test_allocation_order_and_tie_breaking(self):
        """Picks nearest slot first; breaks ties by smaller row then col."""
        # First allocation should pick dist 2 -> (1, 2)
        ok, msg, slot = self.manager.park("KA-01-A", "White")
        self.assertTrue(ok)
        self.assertEqual(slot, Slot(1, 2))

        # Next two both have dist 5: (2, 4) vs (3, 1) -> (2, 4) wins due to smaller row
        ok, msg, slot = self.manager.park("KA-01-B", "Red")
        self.assertTrue(ok)
        self.assertEqual(slot, Slot(2, 4))

        # Third allocation picks (3, 1)
        ok, msg, slot = self.manager.park("KA-01-C", "Blue")
        self.assertTrue(ok)
        self.assertEqual(slot, Slot(3, 1))

    def test_lot_full(self):
        """Returns 'Sorry, parking lot is full' when capacity reached."""
        self.manager.park("CAR-1", "White")
        self.manager.park("CAR-2", "White")
        self.manager.park("CAR-3", "White")

        ok, msg, slot = self.manager.park("CAR-4", "White")
        self.assertFalse(ok)
        self.assertEqual(msg, MSG_LOT_FULL)
        self.assertIsNone(slot)

    def test_leave_then_park_picks_nearest_not_most_recently_freed(self):
        """Crucial requirement: leave then park picks NEAREST free slot, not most recently freed."""
        self.manager.park("CAR-1", "White")  # in (1, 2) [dist 2]
        self.manager.park("CAR-2", "Red")    # in (2, 4) [dist 5]
        self.manager.park("CAR-3", "Blue")   # in (3, 1) [dist 5]

        # Free the farther slot first
        ok, msg = self.manager.leave(2, 4)
        self.assertTrue(ok)
        self.assertEqual(msg, "Slot (2, 4) is free")

        # Now free the closer slot (1, 2)
        ok, msg = self.manager.leave(1, 2)
        self.assertTrue(ok)
        self.assertEqual(msg, "Slot (1, 2) is free")

        # Park a new car: MUST pick (1, 2) [dist 2], NOT (2, 4) [dist 5]
        ok, msg, slot = self.manager.park("CAR-NEW", "Black")
        self.assertTrue(ok)
        self.assertEqual(slot, Slot(1, 2))

    def test_status_empty_lot(self):
        """Empty lot returns 'Parking lot is empty' with no header."""
        lines = self.manager.status()
        self.assertEqual(lines, [MSG_LOT_EMPTY])

    def test_status_ordering_by_row_then_column(self):
        """Status ordering is by (row, col) ascending, NOT by allocation order."""
        # Allocate: (1, 2) first, then (2, 4), then (3, 1)
        # Let's free (1, 2) and leave (2, 4) and (3, 1)
        self.manager.park("CAR-FAR", "Blue")   # (1, 2)
        self.manager.park("CAR-MID", "Red")    # (2, 4)
        self.manager.park("CAR-BOT", "Green")  # (3, 1)

        lines = self.manager.status()
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "Slot Registration No Colour")
        self.assertEqual(lines[1], "(1, 2) CAR-FAR Blue")
        self.assertEqual(lines[2], "(2, 4) CAR-MID Red")
        self.assertEqual(lines[3], "(3, 1) CAR-BOT Green")

    def test_colour_lookups_case_insensitive_and_sorted_by_slot(self):
        """Colour lookup is case-insensitive and results ordered by slot (row, col)."""
        self.manager.park("CAR-1", "White")
        self.manager.park("CAR-2", "WHITE")
        self.manager.park("CAR-3", "white")

        # Query with different casings
        regs = self.manager.registration_numbers_for_colour("wHiTe")
        self.assertEqual(regs, "CAR-1, CAR-2, CAR-3")

        slots = self.manager.slot_numbers_for_colour("WHITE")
        self.assertEqual(slots, "(1, 2), (2, 4), (3, 1)")

        # Not found
        self.assertEqual(
            self.manager.registration_numbers_for_colour("Magenta"),
            MSG_NOT_FOUND,
        )
        self.assertEqual(
            self.manager.slot_numbers_for_colour("Magenta"),
            MSG_NOT_FOUND,
        )

    def test_registration_lookup_case_insensitive(self):
        """Registration lookup is case-insensitive, returns slot or 'Not found'."""
        self.manager.park("ka-01-hh-1234", "White")
        # Lookup using uppercase
        self.assertEqual(
            self.manager.slot_number_for_registration("KA-01-HH-1234"),
            "(1, 2)",
        )
        # Lookup unknown
        self.assertEqual(
            self.manager.slot_number_for_registration("UNKNOWN"),
            MSG_NOT_FOUND,
        )

    def test_car_already_parked_prevented(self):
        """Parking a car with already parked registration fails case-insensitively."""
        ok1, _, slot1 = self.manager.park("KA-01-HH-1234", "White")
        self.assertTrue(ok1)
        self.assertEqual(slot1, Slot(1, 2))

        # Attempt to park again with lower-case
        ok2, msg2, slot2 = self.manager.park("ka-01-hh-1234", "Black")
        self.assertFalse(ok2)
        self.assertEqual(msg2, MSG_CAR_ALREADY_PARKED)
        self.assertIsNone(slot2)
        # Slot count must remain 1 occupied
        self.assertEqual(self.manager.occupied_count, 1)

    def test_leave_already_free_slot_not_pushed_twice(self):
        """Leaving an already free slot returns message and does not duplicate heap entries."""
        ok, msg = self.manager.leave(1, 2)
        self.assertFalse(ok)
        self.assertEqual(msg, MSG_SLOT_ALREADY_FREE.format(r=1, c=2))

        # Park 3 cars: exactly 3 slots should be allocatable, 4th must fail
        self.manager.park("C1", "White")
        self.manager.park("C2", "White")
        self.manager.park("C3", "White")
        ok_extra, msg_extra, _ = self.manager.park("C4", "White")
        self.assertFalse(ok_extra)
        self.assertEqual(msg_extra, MSG_LOT_FULL)

    def test_leave_invalid_slot(self):
        """Leaving a slot that does not exist or is not usable returns 'Invalid slot'."""
        ok, msg = self.manager.leave(99, 99)
        self.assertFalse(ok)
        self.assertEqual(msg, MSG_INVALID_SLOT)


if __name__ == "__main__":
    unittest.main()
