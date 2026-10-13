"""End-to-end golden test verification."""

import os
import subprocess
import unittest


class TestGolden(unittest.TestCase):
    """Verifies that the golden sample produces exact byte-for-byte expected output."""

    def test_golden_sample_exact_output(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        input_path = os.path.join(base_dir, "input.txt")
        expected_path = os.path.join(base_dir, "expected_output.txt")

        # Run via python -m parking_lot input.txt
        proc = subprocess.run(
            ["python", "-m", "parking_lot", input_path],
            cwd=base_dir,
            capture_output=True,
            text=True,
            check=True,
        )

        with open(expected_path, "r", encoding="utf-8") as f:
            expected_output = f.read()

        # Normalize line endings for cross-platform comparison
        actual_normalized = proc.stdout.replace("\r\n", "\n")
        expected_normalized = expected_output.replace("\r\n", "\n")

        self.assertEqual(
            actual_normalized,
            expected_normalized,
            "Golden output did not match byte-for-byte!",
        )


if __name__ == "__main__":
    unittest.main()
