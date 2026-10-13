"""Command processor coordinating parser, grid, and parking manager to produce outputs."""

from typing import List, Optional

from parking_lot.constants import MSG_INVALID_COMMAND, MSG_NOT_CREATED
from parking_lot.grid import DistanceCalculator, GridMap
from parking_lot.manager import ParkingManager
from parking_lot.parser import Command


class CommandProcessor:
    """Executes commands and produces formatted output lines."""

    def __init__(self) -> None:
        self._manager: Optional[ParkingManager] = None

    @property
    def manager(self) -> Optional[ParkingManager]:
        return self._manager

    def process(self, cmd: Command) -> List[str]:
        """Processes a single command and returns one or more output strings."""
        if cmd.error_message:
            return [cmd.error_message]

        if cmd.name == "create_parking_lot":
            rows = int(cmd.args[0])
            cols = int(cmd.args[1])
            grid = GridMap.from_lines(rows, cols, cmd.map_lines)
            usable_slots = DistanceCalculator.calculate_usable_slots(grid)
            # Re-initialise lot completely (new map, clear cars)
            self._manager = ParkingManager(usable_slots)
            return [f"Created a parking lot with {len(usable_slots)} usable slots"]

        # Any command before create_parking_lot -> Parking lot not created
        if self._manager is None:
            return [MSG_NOT_CREATED]

        if cmd.name == "park":
            reg, colour = cmd.args[0], cmd.args[1]
            _, msg, _ = self._manager.park(reg, colour)
            return [msg]

        if cmd.name == "leave":
            r, c = int(cmd.args[0]), int(cmd.args[1])
            _, msg = self._manager.leave(r, c)
            return [msg]

        if cmd.name == "status":
            return self._manager.status()

        if cmd.name == "registration_numbers_for_cars_with_colour":
            colour = cmd.args[0]
            return [self._manager.registration_numbers_for_colour(colour)]

        if cmd.name == "slot_numbers_for_cars_with_colour":
            colour = cmd.args[0]
            return [self._manager.slot_numbers_for_colour(colour)]

        if cmd.name == "slot_number_for_registration_number":
            reg = cmd.args[0]
            return [self._manager.slot_number_for_registration(reg)]

        return [MSG_INVALID_COMMAND]
