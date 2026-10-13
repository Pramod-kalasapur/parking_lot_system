"""Data models for the Parking Lot System."""

from dataclasses import dataclass
from typing import NamedTuple


class Slot(NamedTuple):
    """1-indexed grid coordinate representing a parking slot."""

    row: int
    col: int

    def __str__(self) -> str:
        return f"({self.row}, {self.col})"


class SlotDistance(NamedTuple):
    """Key used for ordering free slots in the min-heap."""

    distance: int
    row: int
    col: int

    @property
    def slot(self) -> Slot:
        return Slot(self.row, self.col)


@dataclass(frozen=True)
class Car:
    """Represents a parked car."""

    registration: str
    colour: str
