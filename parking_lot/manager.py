"""In-memory parking manager handling allocation, state, and indexing with zero I/O."""

from collections import defaultdict
import heapq
from typing import Dict, List, Optional, Set, Tuple

from parking_lot.constants import (
    MSG_CAR_ALREADY_PARKED,
    MSG_INVALID_SLOT,
    MSG_LOT_EMPTY,
    MSG_LOT_FULL,
    MSG_NOT_FOUND,
    MSG_SLOT_ALREADY_FREE,
    MSG_STATUS_HEADER,
)
from parking_lot.models import Car, Slot, SlotDistance


class ParkingManager:
    """Manages slot allocation, occupancy, and fast lookups in memory."""

    def __init__(self, usable_slots: List[SlotDistance]):
        self._usable_count = len(usable_slots)
        # Min-heap of free slots keyed by (distance, row, col)
        self._free_slots: List[SlotDistance] = list(usable_slots)
        heapq.heapify(self._free_slots)

        # Static mapping from Slot -> original distance
        self._slot_distances: Dict[Slot, int] = {
            s.slot: s.distance for s in usable_slots
        }
        # Set of all valid usable slots for O(1) membership check
        self._usable_slots: Set[Slot] = set(self._slot_distances.keys())

        # Current occupancy: Slot -> Car
        self._occupancy: Dict[Slot, Car] = {}

        # Lookups:
        # Uppercase registration -> Slot (case-insensitive search, original case preserved in Car)
        self._reg_index: Dict[str, Slot] = {}
        # Lowercase colour -> Set[Slot] (case-insensitive colour search)
        self._colour_index: Dict[str, Set[Slot]] = defaultdict(set)

    @property
    def usable_count(self) -> int:
        return self._usable_count

    @property
    def occupied_count(self) -> int:
        return len(self._occupancy)

    def park(self, registration: str, colour: str) -> Tuple[bool, str, Optional[Slot]]:
        """Allocates the nearest free slot to a car.

        Returns: (success, message, slot)
        """
        reg_key = registration.upper()
        if reg_key in self._reg_index:
            return False, MSG_CAR_ALREADY_PARKED, None

        if not self._free_slots:
            return False, MSG_LOT_FULL, None

        slot_dist = heapq.heappop(self._free_slots)
        slot = slot_dist.slot
        car = Car(registration=registration, colour=colour)

        self._occupancy[slot] = car
        self._reg_index[reg_key] = slot
        self._colour_index[colour.lower()].add(slot)

        return True, f"Allocated slot: {slot}", slot

    def leave(self, row: int, col: int) -> Tuple[bool, str]:
        """Releases an occupied slot and pushes it back into the min-heap.

        Returns: (success, message)
        """
        slot = Slot(row, col)
        if slot not in self._usable_slots:
            return False, MSG_INVALID_SLOT

        if slot not in self._occupancy:
            return False, MSG_SLOT_ALREADY_FREE.format(r=row, c=col)

        car = self._occupancy.pop(slot)
        del self._reg_index[car.registration.upper()]
        self._colour_index[car.colour.lower()].discard(slot)

        dist = self._slot_distances[slot]
        heapq.heappush(self._free_slots, SlotDistance(dist, row, col))

        return True, f"Slot {slot} is free"

    def status(self) -> List[str]:
        """Returns the current occupancy status formatted as lines."""
        if not self._occupancy:
            return [MSG_LOT_EMPTY]

        lines = [MSG_STATUS_HEADER]
        # Sorted by row, then col ascending
        for slot in sorted(self._occupancy.keys()):
            car = self._occupancy[slot]
            lines.append(f"{slot} {car.registration} {car.colour}")
        return lines

    def registration_numbers_for_colour(self, colour: str) -> str:
        """Finds registration numbers for cars of a given colour, ordered by slot (row, col)."""
        slots = self._colour_index.get(colour.lower())
        if not slots:
            return MSG_NOT_FOUND

        sorted_slots = sorted(slots)
        return ", ".join(self._occupancy[s].registration for s in sorted_slots)

    def slot_numbers_for_colour(self, colour: str) -> str:
        """Finds slot numbers for cars of a given colour, ordered by slot (row, col)."""
        slots = self._colour_index.get(colour.lower())
        if not slots:
            return MSG_NOT_FOUND

        sorted_slots = sorted(slots)
        return ", ".join(str(s) for s in sorted_slots)

    def slot_number_for_registration(self, registration: str) -> str:
        """Finds the slot occupied by the car with given registration number."""
        slot = self._reg_index.get(registration.upper())
        if slot is None:
            return MSG_NOT_FOUND
        return str(slot)
