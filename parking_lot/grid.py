"""Grid map parsing and distance calculations using iterative BFS."""
from typing import List, Optional

from parking_lot.constants import CELL_ENTRANCE, CELL_PARKING, CELL_ROAD, CELL_WALL
from parking_lot.models import SlotDistance


class GridMap:
    """Represents the 2D parking lot grid stored as a flat 1D array."""

    def __init__(self, rows: int, cols: int, cells: List[str], entrance_idx: Optional[int]):
        self.rows = rows
        self.cols = cols
        self.cells = cells
        self.entrance_idx = entrance_idx

    @classmethod
    def from_lines(cls, rows: int, cols: int, raw_lines: List[str]) -> "GridMap":
        """Builds a GridMap from raw text lines, padding/truncating safely."""
        cells: List[str] = []
        entrance_idx: Optional[int] = None

        for r in range(rows):
            line = raw_lines[r] if r < len(raw_lines) else ""
            # Strip trailing newline/whitespace while preserving inner characters
            line = line.strip("\r\n")
            if len(line) < cols:
                # Pad short lines with walls safely
                line = line + CELL_WALL * (cols - len(line))
            elif len(line) > cols:
                # Truncate long lines to specified cols
                line = line[:cols]

            for c, char in enumerate(line):
                idx = r * cols + c
                if char == CELL_ENTRANCE and entrance_idx is None:
                    entrance_idx = idx
                cells.append(char)

        return cls(rows=rows, cols=cols, cells=cells, entrance_idx=entrance_idx)


class DistanceCalculator:
    """Calculates road distances from the entrance and finds all usable parking slots."""

    @staticmethod
    def calculate_usable_slots(grid: GridMap) -> List[SlotDistance]:
        """Runs iterative BFS from E and computes distances for all reachable P slots.

        Cars enter at E and move only on road cells ('.'), 4-directionally.
        Cars never drive THROUGH a P cell (BFS expands only through '.' and E).
        Distance of a slot = min(neighbourDist of reachable road/E) + 1.
        Unreachable slots are ignored.
        """
        rows = grid.rows
        cols = grid.cols
        total_cells = rows * cols
        cells = grid.cells

        if grid.entrance_idx is None or rows <= 0 or cols <= 0:
            return []

        # Distance array for BFS: -1 means unvisited / unreachable
        dist: List[int] = [-1] * total_cells
        dist[grid.entrance_idx] = 0

        # Iterative BFS queue with a head index: O(1) pops without recursion.
        queue: List[int] = [grid.entrance_idx]
        head = 0

        while head < len(queue):
            curr = queue[head]
            head += 1
            curr_dist = dist[curr] + 1
            r = curr // cols
            c = curr % cols

            # 4-directional moves: Up, Down, Left, Right
            # Up
            if r > 0:
                nbr = curr - cols
                if dist[nbr] == -1 and cells[nbr] == CELL_ROAD:
                    dist[nbr] = curr_dist
                    queue.append(nbr)
            # Down
            if r + 1 < rows:
                nbr = curr + cols
                if dist[nbr] == -1 and cells[nbr] == CELL_ROAD:
                    dist[nbr] = curr_dist
                    queue.append(nbr)
            # Left
            if c > 0:
                nbr = curr - 1
                if dist[nbr] == -1 and cells[nbr] == CELL_ROAD:
                    dist[nbr] = curr_dist
                    queue.append(nbr)
            # Right
            if c + 1 < cols:
                nbr = curr + 1
                if dist[nbr] == -1 and cells[nbr] == CELL_ROAD:
                    dist[nbr] = curr_dist
                    queue.append(nbr)

        # Compute slot distances for all 'P' cells
        usable_slots: List[SlotDistance] = []

        for idx, char in enumerate(cells):
            if char != CELL_PARKING:
                continue

            r = idx // cols
            c = idx % cols

            min_neighbour_dist = -1

            # Check 4 neighbours (Up, Down, Left, Right)
            # Up
            if r > 0:
                nbr = idx - cols
                if cells[nbr] in (CELL_ROAD, CELL_ENTRANCE) and dist[nbr] != -1:
                    if min_neighbour_dist == -1 or dist[nbr] < min_neighbour_dist:
                        min_neighbour_dist = dist[nbr]
            # Down
            if r + 1 < rows:
                nbr = idx + cols
                if cells[nbr] in (CELL_ROAD, CELL_ENTRANCE) and dist[nbr] != -1:
                    if min_neighbour_dist == -1 or dist[nbr] < min_neighbour_dist:
                        min_neighbour_dist = dist[nbr]
            # Left
            if c > 0:
                nbr = idx - 1
                if cells[nbr] in (CELL_ROAD, CELL_ENTRANCE) and dist[nbr] != -1:
                    if min_neighbour_dist == -1 or dist[nbr] < min_neighbour_dist:
                        min_neighbour_dist = dist[nbr]
            # Right
            if c + 1 < cols:
                nbr = idx + 1
                if cells[nbr] in (CELL_ROAD, CELL_ENTRANCE) and dist[nbr] != -1:
                    if min_neighbour_dist == -1 or dist[nbr] < min_neighbour_dist:
                        min_neighbour_dist = dist[nbr]

            if min_neighbour_dist != -1:
                # 1-indexed row and column
                slot_distance = min_neighbour_dist + 1
                usable_slots.append(
                    SlotDistance(distance=slot_distance, row=r + 1, col=c + 1)
                )

        return usable_slots
