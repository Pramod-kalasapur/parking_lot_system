"""Performance test for 1000x1000 grid and 100,000 commands."""

import time
import unittest

from parking_lot.parser import Command
from parking_lot.processor import CommandProcessor


class TestPerformance(unittest.TestCase):
    """Verifies that 1000x1000 grid + 100,000 commands complete in a few seconds."""

    def test_1000x1000_grid_and_100k_commands(self):
        rows, cols = 1000, 1000
        map_lines = []
        # Entrance on row 0, followed by roads
        map_lines.append("E" + "." * (cols - 1))
        # Alternating parking rows with vertical corridors on edges
        for r in range(1, rows):
            if r % 2 == 1:
                map_lines.append("." + "P" * (cols - 2) + ".")
            else:
                map_lines.append("." * cols)

        processor = CommandProcessor()

        start_time = time.perf_counter()

        # 1. Create parking lot
        init_cmd = Command(
            name="create_parking_lot",
            args=[str(rows), str(cols)],
            map_lines=map_lines,
        )
        out = processor.process(init_cmd)
        self.assertEqual(len(out), 1)
        self.assertIn("Created a parking lot with 499000 usable slots", out[0])

        bfs_time = time.perf_counter()

        # 2. Run 100,000 mixed commands
        # 50,000 park operations
        for i in range(50000):
            cmd = Command(
                name="park",
                args=[f"KA-{i:06d}", "White" if i % 2 == 0 else "Black"],
            )
            processor.process(cmd)

        # 25,000 leave operations
        for i in range(25000):
            # Slots in row 2 (1-indexed), cols 2..999
            col = (i % (cols - 2)) + 2
            cmd = Command(name="leave", args=["2", str(col)])
            processor.process(cmd)

        # 15,000 registration lookups
        for i in range(15000):
            cmd = Command(
                name="slot_number_for_registration_number",
                args=[f"KA-{i:06d}"],
            )
            processor.process(cmd)

        # 10,000 colour lookups
        for _ in range(10000):
            cmd = Command(
                name="slot_number_for_registration_number",
                args=["KA-000010"],
            )
            processor.process(cmd)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        command_time = end_time - bfs_time

        print(
            f"\n[Performance Benchmark] 1000x1000 grid (499,000 usable slots) BFS: "
            f"{bfs_time - start_time:.3f}s | 100k commands: {command_time:.3f}s | "
            f"Total: {total_time:.3f}s"
        )

        # Generous threshold: must finish within 10 seconds
        self.assertLess(
            total_time,
            10.0,
            f"Performance test took {total_time:.2f}s, expected under 10.0s",
        )


if __name__ == "__main__":
    unittest.main()
