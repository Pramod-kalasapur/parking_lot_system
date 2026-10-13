"""Unit tests for Section 5 edge cases and invalid input robustness."""

import unittest

from parking_lot.constants import (
    MSG_INVALID_COMMAND,
    MSG_LOT_FULL,
    MSG_NOT_CREATED,
)
from parking_lot.parser import CommandParser
from parking_lot.processor import CommandProcessor


class TestEdgeCasesAndInvalidInputs(unittest.TestCase):
    """Ensures the program never crashes on invalid inputs as specified in Section 5."""

    def test_command_before_create_parking_lot(self):
        """Any command before create_parking_lot returns 'Parking lot not created'."""
        processor = CommandProcessor()
        stream = iter(["park KA-01-HH-1234 White", "status", "leave 1 2"])
        outputs = []
        for cmd in CommandParser.parse_stream(stream):
            outputs.extend(processor.process(cmd))

        self.assertEqual(outputs, [MSG_NOT_CREATED, MSG_NOT_CREATED, MSG_NOT_CREATED])

    def test_second_create_parking_lot_reinitializes_system(self):
        """A second create_parking_lot completely re-initializes lot and clears existing cars."""
        processor = CommandProcessor()
        commands = [
            "create_parking_lot 1 2\n",
            "EP\n",
            "park KA-01 White\n",
            "create_parking_lot 1 3\n",
            "E.P\n",
            "status\n",
            "slot_number_for_registration_number KA-01\n",
        ]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(commands)):
            outputs.extend(processor.process(cmd))

        expected = [
            "Created a parking lot with 1 usable slots",
            "Allocated slot: (1, 2)",
            "Created a parking lot with 1 usable slots",
            "Parking lot is empty",
            "Not found",
        ]
        self.assertEqual(outputs, expected)

    def test_case_sensitivity_of_command_names(self):
        """Command words are matched case-sensitively; wrong case -> 'Invalid command'."""
        processor = CommandProcessor()
        # Initialize parking lot first
        for cmd in CommandParser.parse_stream(iter(["create_parking_lot 1 2", "EP"])):
            processor.process(cmd)

        commands = ["Park KA-01 White", "STATUS", "Leave 1 2", "foo_bar"]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(commands)):
            outputs.extend(processor.process(cmd))

        self.assertEqual(outputs, [MSG_INVALID_COMMAND] * 4)

    def test_wrong_argument_counts_and_types(self):
        """Wrong argument count or non-integer row/col returns 'Invalid command'."""
        processor = CommandProcessor()
        for cmd in CommandParser.parse_stream(iter(["create_parking_lot 1 2", "EP"])):
            processor.process(cmd)

        invalid_commands = [
            "create_parking_lot 1",            # Missing cols
            "create_parking_lot a b",          # Non-integer
            "create_parking_lot -1 2",         # Negative rows
            "park KA-01",                      # Missing colour
            "park KA-01 White Extra",          # Extra token (multi-word colour)
            "leave 1",                         # Missing col
            "leave a b",                       # Non-integer
            "status extra",                    # Extra argument
            "registration_numbers_for_cars_with_colour",  # Missing arg
            "slot_numbers_for_cars_with_colour",          # Missing arg
            "slot_number_for_registration_number",        # Missing arg
        ]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(invalid_commands)):
            outputs.extend(processor.process(cmd))

        self.assertEqual(outputs, [MSG_INVALID_COMMAND] * len(invalid_commands))

    def test_blank_lines_and_whitespace_ignored(self):
        """Blank lines and extra whitespace do not produce errors or output."""
        processor = CommandProcessor()
        commands = [
            "\n",
            "   \n",
            "create_parking_lot   1   2  \n",
            "EP\n",
            "\n",
            "   park   KA-01    White   \n",
            "\n",
        ]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(commands)):
            outputs.extend(processor.process(cmd))

        self.assertEqual(
            outputs,
            [
                "Created a parking lot with 1 usable slots",
                "Allocated slot: (1, 2)",
            ],
        )

    def test_map_lines_short_long_missing_safely_handled(self):
        """Map lines shorter or longer than cols, or missing rows, handled safely without crash."""
        processor = CommandProcessor()
        # Cols is 4, but line 1 is only 2 chars ('EP'), line 2 is missing entirely
        commands = [
            "create_parking_lot 2 4\n",
            "EP\n",
            # Missing second line
        ]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(commands)):
            outputs.extend(processor.process(cmd))

        # EP is padded with '##' -> 'EP##', row 2 is '####'. Slot (1, 2) is usable!
        self.assertEqual(outputs, ["Created a parking lot with 1 usable slots"])

    def test_zero_usable_slots(self):
        """When all slots are blocked, create prints 0 usable slots, park prints full."""
        processor = CommandProcessor()
        commands = [
            "create_parking_lot 2 2\n",
            "E#\n",
            "#P\n",
            "park KA-01 White\n",
        ]
        outputs = []
        for cmd in CommandParser.parse_stream(iter(commands)):
            outputs.extend(processor.process(cmd))

        self.assertEqual(
            outputs,
            [
                "Created a parking lot with 0 usable slots",
                MSG_LOT_FULL,
            ],
        )


if __name__ == "__main__":
    unittest.main()
