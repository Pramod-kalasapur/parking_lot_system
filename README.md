# Parking Lot System

A command-line parking lot management system built with Python. The project models a real parking lot as a 2D grid of roads, walls, an entrance, and parking slots. It uses Breadth-First Search to find reachable slots and always allocates the nearest available parking slot.

This project is designed to demonstrate clean code structure, algorithmic thinking, defensive input handling, and test-driven verification.

## Key Features

- Creates a parking lot dynamically from a grid input.
- Finds the nearest reachable parking slot from the entrance.
- Uses BFS for shortest-path distance calculation.
- Uses a min-heap for efficient nearest-slot allocation.
- Supports parking, leaving, status display, and search commands.
- Handles invalid commands without crashing.
- Supports both file-based input and manual terminal input.
- Includes a full unit test suite and performance test.
- Uses only the Python standard library.

## Problem Overview

The parking lot is represented as a grid:

| Symbol | Meaning |
| --- | --- |
| `E` | Entrance |
| `.` | Road |
| `#` | Wall |
| `P` | Parking slot |

Cars enter from `E` and can move only on road cells. Movement is allowed in four directions: up, down, left, and right. Cars cannot move diagonally and cannot drive through parking slots.

A parking slot is usable only if it is directly next to the entrance or to a reachable road cell.

## Example Grid

```text
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
```

In this grid:

- `E` is the entrance.
- `.` cells are roads.
- `#` cells are walls.
- `P` cells are parking slots.
- Some `P` cells may be unreachable and are not counted as usable slots.

For the sample grid, there are 12 `P` cells, but only 10 usable slots.

## How Slot Allocation Works

The system calculates the distance of every usable parking slot from the entrance.

Slot distance:

```text
distance from E to nearest adjacent reachable road cell + 1 step into the slot
```

When a car parks, the system chooses the free slot with the smallest:

```text
(distance, row, column)
```

This means:

1. Nearest slot is selected first.
2. If distances are equal, the smaller row wins.
3. If rows are also equal, the smaller column wins.

Rows and columns are 1-indexed.

### Slot Allocation Decision Flow

```text
                      [ Incoming Park Request ]
                                  │
                                  ▼
                   Is Registration Already Parked?
                     /                         \
                   (Yes)                       (No)
                    /                             \
        [ "Car already parked" ]           Is Min-Heap Empty?
                                            /              \
                                          (Yes)            (No)
                                           /                  \
                            [ "Sorry, parking lot is full" ]   heappop(Min-Heap)
                                                                (Picks smallest:
                                                                 dist -> row -> col)
                                                                      │
                                                                      ▼
                                                                Allocate Slot:
                                                                • Store in Occupancy
                                                                • Add to Reg Map
                                                                • Add to Colour Set
                                                                      │
                                                                      ▼
                                                          [ "Allocated slot: (r, c)" ]
```

## Supported Commands

| Command | Description |
| --- | --- |
| `create_parking_lot <rows> <cols>` | Creates the parking lot. The next `<rows>` lines are the map. |
| `park <registration_number> <colour>` | Parks a car in the nearest available slot. |
| `leave <row> <col>` | Frees the given parking slot. |
| `status` | Shows all parked cars sorted by row, then column. |
| `registration_numbers_for_cars_with_colour <colour>` | Lists registration numbers for cars with the given colour. |
| `slot_numbers_for_cars_with_colour <colour>` | Lists slots occupied by cars with the given colour. |
| `slot_number_for_registration_number <registration_number>` | Finds the slot for a registration number. |

Colour matching is case-insensitive. Registration lookup is also case-insensitive.

## Sample Input

```text
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park KA-01-HH-1234 White
park KA-01-HH-9999 White
park KA-01-BB-0001 Black
park KA-01-HH-7777 Red
park KA-01-HH-2701 Blue
park KA-01-HH-3141 Black
park KA-01-HH-5555 Grey
park KA-01-HH-6666 White
park KA-01-HH-8888 Red
park KA-01-HH-1111 Blue
leave 1 7
leave 2 1
status
park KA-01-P-333 White
park DL-12-AA-9999 White
park MH-04-AY-1111 Black
registration_numbers_for_cars_with_colour White
slot_numbers_for_cars_with_colour White
slot_number_for_registration_number KA-01-HH-3141
slot_number_for_registration_number MH-04-AY-1111
slot_number_for_registration_number TN-07-ZZ-0000
```

## Sample Output

```text
Created a parking lot with 10 usable slots
Allocated slot: (2, 1)
Allocated slot: (2, 3)
Allocated slot: (2, 5)
Allocated slot: (1, 7)
Allocated slot: (2, 7)
Allocated slot: (4, 7)
Allocated slot: (4, 4)
Allocated slot: (5, 7)
Allocated slot: (3, 1)
Allocated slot: (4, 2)
Slot (1, 7) is free
Slot (2, 1) is free
Slot Registration No Colour
(2, 3) KA-01-HH-9999 White
(2, 5) KA-01-BB-0001 Black
(2, 7) KA-01-HH-2701 Blue
(3, 1) KA-01-HH-8888 Red
(4, 2) KA-01-HH-1111 Blue
(4, 4) KA-01-HH-5555 Grey
(4, 7) KA-01-HH-3141 Black
(5, 7) KA-01-HH-6666 White
Allocated slot: (2, 1)
Allocated slot: (1, 7)
Sorry, parking lot is full
DL-12-AA-9999, KA-01-P-333, KA-01-HH-9999, KA-01-HH-6666
(1, 7), (2, 1), (2, 3), (5, 7)
(4, 7)
Not found
Not found
```

## How to Run

Open PowerShell in the project folder:

```powershell
cd C:\Users\Pramod\Documents\Parking_Lot_System
```

Run with the sample input file:

```powershell
python main.py input.txt
```

You can also run it as a Python module:

```powershell
python -m parking_lot input.txt
```

## Manual Input Mode

You can enter commands manually in the terminal:

```powershell
python main.py
```

Then type:

```text
create_parking_lot 5 7
E.....P
P#P#P.P
P.....#
PP#P#.P
P####.P
park KA-01-HH-1234 White
status
```

To finish manual input in PowerShell, press:

```text
Ctrl+Z
```

Then press `Enter`.

## Project Structure

```text
Parking_Lot_System/
  main.py
  input.txt
  expected_output.txt
  README.md
  .gitignore
  parking_lot/
    __init__.py
    __main__.py
    constants.py
    grid.py
    main.py
    manager.py
    models.py
    parser.py
    processor.py
  tests/
    __init__.py
    test_edge_cases.py
    test_golden.py
    test_grid.py
    test_manager.py
    test_parking_lot.py
    test_performance.py
```

## Architecture

The code is separated into small modules with clear responsibilities.

| File | Responsibility |
| --- | --- |
| `parking_lot/constants.py` | Stores output messages and grid symbols. |
| `parking_lot/models.py` | Defines `Slot`, `SlotDistance`, and `Car`. |
| `parking_lot/grid.py` | Builds the grid and calculates usable slots with BFS. |
| `parking_lot/manager.py` | Handles parking, leaving, status, and searches. |
| `parking_lot/parser.py` | Parses command input safely. |
| `parking_lot/processor.py` | Connects parsed commands to business logic. |
| `parking_lot/main.py` | CLI entry point and input/output handling. |
| `main.py` | Simple root launcher. |

### System Architecture Diagram

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        1. CLI & INPUT LAYER                            │
│   • File mode: python main.py input.txt                                │
│   • Manual / Piped: python main.py                                     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Lines Stream
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   2. PARSER & TOKENIZER (parser.py)                    │
│   • CommandParser: Cleans whitespace, validates argument counts/types  │
│   • Yields validated Command(name, args, map_lines)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Command Objects
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│               3. ORCHESTRATION & FORMATTING (processor.py)             │
│   • CommandProcessor: Coordinates between Grid and ParkingManager      │
│   • Formats results into output strings                                │
└───────────────┬───────────────────────────────────────┬────────────────┘
                │ create_parking_lot                    │ park / leave / status
                ▼                                       ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│  4. GRID & GRAPH ENGINE (grid.py)    │  │ 5. STATE MANAGER (manager.py)│
│                                      │  │    (Pure In-Memory, Zero I/O)│
│  • GridMap:                          │  │                              │
│    Flat 1D array (r * cols + c)      │  │  ┌────────────────────────┐  │
│                                      │  │  │ Min-Heap (Free Slots)  │  │
│  • DistanceCalculator:               │  │  │ Key: (dist, row, col)  │  │
│    Iterative BFS from Entrance 'E'   │  │  └────────────────────────┘  │
│    (Expands only on '.' roads)       │  │  ┌────────────────────────┐  │
│                                      │  │  │ Occupancy Map          │  │
│  • Slot Reachability:                │  │  │ Slot -> (Reg, Colour)  │  │
│    dist = min(road_neighbours) + 1   │  │  └────────────────────────┘  │
│    (Filters out unreachable slots)   │  │  ┌────────────────────────┐  │
│                                      │  │  │ Inverted Hash Indexes  │  │
│                                      │  │  │ • Reg (Upper) -> Slot  │  │
│                                      │  │  │ • Colour -> Set[Slots] │  │
│                                      │  │  └────────────────────────┘  │
└──────────────────┬───────────────────┘  └──────────────┬───────────────┘
                   │ Usable Slots [(dist, r, c)]         │
                   └─────────────────────────────────────┘
```

### End-to-End Execution Flow

```text
Step 1: Create Parking Lot
User Input:
  create_parking_lot 5 7
  E.....P
  P#P#P.P
  P.....#
  PP#P#.P
  P####.P
Flow:
  main.py ──> parser.py ──> processor.py ──> grid.py (BFS) ──> manager.py
Result:
  "Created a parking lot with 10 usable slots"

Step 2: Park a Car
User Input:
  park KA-01-HH-1234 White
Flow:
  main.py ──> processor.py ──> manager.py (heappop nearest free slot: (2, 1))
Result:
  "Allocated slot: (2, 1)"

Step 3: Free a Slot
User Input:
  leave 2 1
Flow:
  main.py ──> processor.py ──> manager.py (heappush slot (2, 1) back into heap)
Result:
  "Slot (2, 1) is free"

Step 4: Check Status
User Input:
  status
Flow:
  main.py ──> processor.py ──> manager.py (Sorts occupied slots by row, then col)
Result:
  Slot    Registration No    Colour
  (2, 3)  KA-01-HH-9999      White
  (2, 5)  KA-01-BB-0001      Black
```

## Algorithm Details

### 1. Grid Representation

The grid is stored as a flat array:

```text
index = row * columns + column
```

This keeps indexing simple and efficient for large maps.

### 2. BFS Distance Calculation

The system runs Breadth-First Search from the entrance.

BFS expands only through:

- `E`
- `.`

It does not expand through:

- `P`
- `#`

This ensures that cars do not drive through parking slots or walls.

### 3. Usable Slot Detection

After BFS, every `P` cell checks its four neighbours. If any neighbour is a reachable road or the entrance, the slot is usable.

Unreachable parking slots are ignored.

### 4. Fast Parking Allocation

Free parking slots are stored in a min-heap:

```text
(distance, row, column)
```

This allows the nearest available slot to be selected efficiently.

### 5. Fast Search Indexes

The system keeps indexes for quick lookup:

```text
registration -> slot
colour -> set of slots
slot -> car
```

This makes registration lookup fast and keeps colour searches simple and reliable.

## Complexity

| Operation | Time Complexity |
| --- | --- |
| Build grid and run BFS | `O(rows * cols)` |
| Discover usable slots | `O(rows * cols)` |
| Park a car | `O(log K)` |
| Leave a slot | `O(log K)` |
| Search by registration | `O(1)` |
| Search by colour | `O(k log k)` |
| Status | `O(m log m)` |

Where:

- `K` is the number of usable parking slots.
- `k` is the number of cars matching a colour.
- `m` is the number of currently parked cars.

## Invalid Input Handling

The program is designed to continue safely when input is invalid.

| Situation | Output |
| --- | --- |
| Unknown command | `Invalid command` |
| Wrong number of arguments | `Invalid command` |
| Non-integer row or column | `Invalid command` |
| Command before lot creation | `Parking lot not created` |
| Parking same registration again | `Car already parked` |
| Parking when full | `Sorry, parking lot is full` |
| Leaving an invalid slot | `Invalid slot` |
| Leaving an already free usable slot | `Slot (r, c) is already free` |
| Search with no result | `Not found` |
| Status when empty | `Parking lot is empty` |

## Testing

Run all tests:

```powershell
python -m unittest discover -s tests
```

Run tests with detailed output:

```powershell
python -m unittest discover -s tests -v
```

The test suite covers:

- Exact sample input/output verification.
- BFS distance calculation.
- Unreachable parking slots.
- Tie-breaking by row and column.
- Parking and leaving behaviour.
- Case-insensitive colour and registration lookup.
- Invalid input handling.
- Empty parking lot status.
- Full parking lot handling.
- Large grid performance.

## Verified Result

Latest verification:

```text
Ran 43 tests
OK
```

Performance test:

```text
1000 x 1000 grid
100,000 commands
Completed in a few seconds
```

## What This Project Demonstrates

This project demonstrates:

- Graph traversal using BFS.
- Priority queue usage with `heapq`.
- Hash-map based indexing.
- Clean separation of concerns.
- Command-line application design.
- Defensive programming.
- Unit testing with Python `unittest`.
- Performance-aware implementation for large input sizes.

## Tech Stack

- Language: Python 3.11+
- Libraries: Python standard library only
- Testing: `unittest`
- Interface: Command line


