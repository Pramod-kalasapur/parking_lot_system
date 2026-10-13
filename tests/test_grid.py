"""Unit tests for GridMap and DistanceCalculator."""

import unittest

from parking_lot.grid import DistanceCalculator, GridMap
from parking_lot.models import Slot, SlotDistance


class TestGridAndDistances(unittest.TestCase):
    """Verifies BFS road calculations, slot reachability, and tie-breaking rules."""

    def test_sample_map_verification_facts(self):
        """Validates all verification facts from Section 3 specification."""
        raw_map = [
            "E.....P",
            "P#P#P.P",
            "P.....#",
            "PP#P#.P",
            "P####.P",
        ]
        grid = GridMap.from_lines(5, 7, raw_map)
        usable_slots = DistanceCalculator.calculate_usable_slots(grid)

        # 12 'P' cells on map but only 10 usable: (4, 1) and (5, 1) are walled in
        self.assertEqual(len(usable_slots), 10)

        # Create mapping of Slot -> distance
        dist_map = {Slot(s.row, s.col): s.distance for s in usable_slots}

        # Check distances from specification
        expected_distances = {
            Slot(2, 1): 1,
            Slot(2, 3): 3,
            Slot(2, 5): 5,
            Slot(1, 7): 6,
            Slot(2, 7): 7,
            Slot(4, 7): 9,
            Slot(4, 4): 10,
            Slot(5, 7): 10,
            Slot(3, 1): 12,
            Slot(4, 2): 12,
        }
        self.assertEqual(dist_map, expected_distances)

        # Unreachable slots must not be present
        self.assertNotIn(Slot(4, 1), dist_map)
        self.assertNotIn(Slot(5, 1), dist_map)

    def test_slot_directly_adjacent_to_entrance(self):
        """Slot directly adjacent to E has distance 1."""
        raw_map = [
            "EP",
        ]
        grid = GridMap.from_lines(1, 2, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        self.assertEqual(len(usable), 1)
        self.assertEqual(usable[0], SlotDistance(distance=1, row=1, col=2))

    def test_cars_do_not_path_through_p_cells(self):
        """BFS expands only through '.' and E; cars never path through 'P'."""
        raw_map = [
            "EPP",
        ]
        grid = GridMap.from_lines(1, 3, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)

        # First P at (1, 2) is adjacent to E -> dist 1
        # Second P at (1, 3) is only adjacent to (1, 2) which is P -> unreachable!
        self.assertEqual(len(usable), 1)
        self.assertEqual(usable[0], SlotDistance(distance=1, row=1, col=2))

    def test_walls_blocking_geometric_nearness(self):
        """Slot geographically near E but separated by wall is unreachable or takes long path."""
        # Walled-off slot
        raw_map = [
            "E#P",
            ".#.",
        ]
        grid = GridMap.from_lines(2, 3, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        # (1, 3) is adjacent to '#' and '.', where '.' at (2, 3) is unreachable from E
        # Road from E goes to (2, 1), but (2, 2) is '#', so (2, 3) is unreachable
        self.assertEqual(len(usable), 0)

        # Path around wall
        raw_map_around = [
            "E#P",
            "...",
        ]
        # Path: (1,1)[E]=0 -> (2,1)[.]=1 -> (2,2)[.]=2 -> (2,3)[.]=3 -> (1,3)[P]=4
        grid_around = GridMap.from_lines(2, 3, raw_map_around)
        usable_around = DistanceCalculator.calculate_usable_slots(grid_around)
        self.assertEqual(len(usable_around), 1)
        self.assertEqual(usable_around[0], SlotDistance(distance=4, row=1, col=3))

    def test_slot_touching_multiple_roads_uses_smaller_distance(self):
        """If a slot touches multiple reachable road cells, smallest distance + 1 is used."""
        # (1, 1) is E (dist 0)
        # (1, 2) is . (dist 1)
        # (2, 2) is . (dist 2)
        # (2, 1) is P: adjacent to (1, 1) [dist 0] and (2, 2) [dist 2]
        # Min neighbour is 0 -> slot distance = 0 + 1 = 1
        raw_map = [
            "E.",
            "P.",
        ]
        grid = GridMap.from_lines(2, 2, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        self.assertEqual(len(usable), 1)
        self.assertEqual(usable[0], SlotDistance(distance=1, row=2, col=1))

    def test_tie_break_ordering(self):
        """When distances tie, smaller row wins; if rows tie, smaller col wins."""
        raw_map = [
            "P.P",
            ".E.",
            "P.P",
        ]
        grid = GridMap.from_lines(3, 3, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        # E is at (2, 2) (dist 0).
        # Road cells: (1, 2) dist 1, (2, 1) dist 1, (2, 3) dist 1, (3, 2) dist 1.
        # Slots are all corners: (1, 1), (1, 3), (3, 1), (3, 3).
        # All have neighbour dist 1 -> all slot dist = 2.
        sorted_usable = sorted(usable)
        expected_order = [
            SlotDistance(distance=2, row=1, col=1),
            SlotDistance(distance=2, row=1, col=3),
            SlotDistance(distance=2, row=3, col=1),
            SlotDistance(distance=2, row=3, col=3),
        ]
        self.assertEqual(sorted_usable, expected_order)

    def test_zero_usable_slots(self):
        """Lot with only walls and unreachable slots produces zero usable slots."""
        raw_map = [
            "E##",
            "###",
            "##P",
        ]
        grid = GridMap.from_lines(3, 3, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        self.assertEqual(len(usable), 0)

    def test_missing_entrance_handled_safely(self):
        """If entrance E is missing, returns 0 usable slots without crashing."""
        raw_map = [
            "...",
            ".P.",
        ]
        grid = GridMap.from_lines(2, 3, raw_map)
        usable = DistanceCalculator.calculate_usable_slots(grid)
        self.assertEqual(len(usable), 0)


if __name__ == "__main__":
    unittest.main()
