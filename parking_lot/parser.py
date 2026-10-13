"""Command parser and input stream reader."""

from dataclasses import dataclass, field
from typing import Iterator, List, Optional

from parking_lot.constants import MSG_INVALID_COMMAND


@dataclass
class Command:
    """Represents a validated or raw parsed command."""

    name: str
    args: List[str] = field(default_factory=list)
    map_lines: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class CommandParser:
    """Parses text lines into executable Command objects."""

    VALID_COMMANDS = {
        "create_parking_lot",
        "park",
        "leave",
        "status",
        "registration_numbers_for_cars_with_colour",
        "slot_numbers_for_cars_with_colour",
        "slot_number_for_registration_number",
    }

    @classmethod
    def parse_stream(cls, line_iterator: Iterator[str]) -> Iterator[Command]:
        """Reads lines from an iterator, ignoring blanks and trimming whitespace."""
        for raw_line in line_iterator:
            line = raw_line.strip()
            if not line:
                continue

            tokens = line.split()
            cmd_name = tokens[0]

            if cmd_name not in cls.VALID_COMMANDS:
                yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                continue

            if cmd_name == "create_parking_lot":
                if len(tokens) != 3:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue

                try:
                    rows = int(tokens[1])
                    cols = int(tokens[2])
                    if rows <= 0 or cols <= 0:
                        yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                        continue
                except ValueError:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue

                # Read next <rows> lines for the map
                map_lines: List[str] = []
                for _ in range(rows):
                    try:
                        map_line = next(line_iterator)
                        map_lines.append(map_line.rstrip("\r\n"))
                    except StopIteration:
                        # Missing lines are padded safely
                        break

                yield Command(
                    name=cmd_name,
                    args=[str(rows), str(cols)],
                    map_lines=map_lines,
                )

            elif cmd_name == "park":
                # Multi-word colours are not supported: colour is single token after reg
                if len(tokens) != 3:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue
                yield Command(name=cmd_name, args=tokens[1:])

            elif cmd_name == "leave":
                if len(tokens) != 3:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue
                try:
                    int(tokens[1])
                    int(tokens[2])
                except ValueError:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue
                yield Command(name=cmd_name, args=tokens[1:])

            elif cmd_name == "status":
                if len(tokens) != 1:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue
                yield Command(name=cmd_name, args=[])

            elif cmd_name in (
                "registration_numbers_for_cars_with_colour",
                "slot_numbers_for_cars_with_colour",
                "slot_number_for_registration_number",
            ):
                if len(tokens) != 2:
                    yield Command(name=cmd_name, error_message=MSG_INVALID_COMMAND)
                    continue
                yield Command(name=cmd_name, args=tokens[1:])
