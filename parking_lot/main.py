"""CLI entry point for the Parking Lot System."""

import os
import sys
from typing import Iterator, List

from parking_lot.parser import CommandParser
from parking_lot.processor import CommandProcessor


def run_stream(line_stream: Iterator[str], is_interactive: bool = False) -> None:
    """Processes commands from any line stream (file, stdin, pipe)."""
    processor = CommandProcessor()
    output_lines: List[str] = []

    for cmd in CommandParser.parse_stream(line_stream):
        results = processor.process(cmd)
        if is_interactive:
            for line in results:
                print(line, flush=True)
        else:
            output_lines.extend(results)

    if not is_interactive and output_lines:
        sys.stdout.buffer.write(("\n".join(output_lines) + "\n").encode("utf-8"))


def run(file_path: str) -> None:
    """Reads commands from input file and prints results to stdout."""
    if not os.path.isfile(file_path):
        sys.stderr.write(f"Error: File not found: {file_path}\n")
        sys.exit(1)

    with open(file_path, "r", encoding="utf-8") as f:
        run_stream(f, is_interactive=False)


def main() -> None:
    """Main CLI entrypoint. Supports both `<cmd> input.txt` and interactive/piped stdin."""
    try:
        if len(sys.argv) >= 2:
            run(sys.argv[1])
        else:
            # If no file argument is given, read from standard input
            is_interactive = sys.stdin.isatty()
            run_stream(sys.stdin, is_interactive=is_interactive)
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
