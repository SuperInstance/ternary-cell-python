"""
ternary-cell-python — Faithful Python port of ternary-cell (Rust).

Cellular computing with ternary tick cycles.
Pure Python, zero dependencies.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Set, Tuple


class TernaryMessenger(Enum):
    """Ternary messenger signal between cells."""

    SIGNAL = 1
    SILENCE = 0
    SUPPRESS = -1

    def to_ternary(self) -> int:
        return self.value

    @staticmethod
    def from_ternary(v: int) -> Optional["TernaryMessenger"]:
        mapping = {1: TernaryMessenger.SIGNAL, 0: TernaryMessenger.SILENCE, -1: TernaryMessenger.SUPPRESS}
        return mapping.get(v)

    @staticmethod
    def combine(a: "TernaryMessenger", b: "TernaryMessenger") -> "TernaryMessenger":
        """Combine two messengers (max wins)."""
        v = max(a.to_ternary(), b.to_ternary())
        return TernaryMessenger.from_ternary(v)  # type: ignore


class CellState(Enum):
    """Cell state in the lifecycle."""

    ACTIVE = "active"
    APOPTOTIC = "apoptotic"
    DIVIDING = "dividing"


class TernaryCell:
    """A single ternary cell with internal state and tick lifecycle.

    Faithful port of Rust ternary-cell TernaryCell.
    """

    def __init__(self, id: int, energy: int = 10, ternary_value: int = 0) -> None:
        self.id: int = id
        self.energy: int = energy
        self.state: CellState = CellState.ACTIVE
        self.ternary_value: int = max(-1, min(1, ternary_value))
        self._prediction: int = 0
        self.surprise: int = 0
        self.inbox: List[TernaryMessenger] = []
        self.tick_count: int = 0
        self.generation: int = 0

    # ------------------------------------------------------------------
    # Lifecycle phases
    # ------------------------------------------------------------------

    def receive(self, msg: TernaryMessenger) -> None:
        """Receive a messenger signal."""
        self.inbox.append(msg)

    def predict(self) -> None:
        """Phase 1: Predict next ternary value based on inbox."""
        combined = sum(m.to_ternary() for m in self.inbox)
        if combined > 0:
            self._prediction = 1
        elif combined < 0:
            self._prediction = -1
        else:
            self._prediction = self.ternary_value

    def perceive(self) -> None:
        """Phase 2: Update value based on combined signals."""
        combined = sum(m.to_ternary() for m in self.inbox)
        if combined != 0:
            self.ternary_value = max(-1, min(1, combined))

    def compute_surprise(self) -> int:
        """Phase 3: Compute surprise (prediction error)."""
        self.surprise = abs(self.ternary_value - self._prediction)
        return self.surprise

    def vibe(self) -> None:
        """Phase 4: Adjust energy based on surprise."""
        self.energy -= self.surprise
        if self.surprise == 0:
            self.energy += 1

    def gc(self) -> None:
        """Phase 5: Clear inbox."""
        self.inbox.clear()

    def conservation(self) -> None:
        """Phase 6: Enforce energy bounds and check apoptosis."""
        self.energy = max(0, min(20, self.energy))
        if self.energy == 0:
            self.state = CellState.APOPTOTIC
        self.tick_count += 1

    def tick(self) -> int:
        """Run a full tick cycle. Returns surprise value."""
        self.predict()
        self.perceive()
        surprise = self.compute_surprise()
        self.vibe()
        self.gc()
        self.conservation()
        return surprise

    # ------------------------------------------------------------------
    # Division & emission
    # ------------------------------------------------------------------

    def can_divide(self) -> bool:
        return self.energy >= 10 and self.state == CellState.ACTIVE

    def divide(self, daughter_id: int) -> Optional["TernaryCell"]:
        """Divide: create a daughter cell, halve energy."""
        if not self.can_divide():
            return None
        self.energy //= 2
        self.state = CellState.DIVIDING
        daughter = TernaryCell(
            id=daughter_id,
            energy=self.energy,
            ternary_value=self.ternary_value,
        )
        daughter._prediction = self.ternary_value
        daughter.generation = self.generation + 1
        return daughter

    def emit(self) -> TernaryMessenger:
        """Emit current value as a messenger."""
        result = TernaryMessenger.from_ternary(self.ternary_value)
        return result if result is not None else TernaryMessenger.SILENCE

    def is_alive(self) -> bool:
        return self.state != CellState.APOPTOTIC


class CellGrid:
    """A 2D grid of ternary cells with 4-connected neighbor signaling."""

    def __init__(self, width: int, height: int) -> None:
        self.width: int = width
        self.height: int = height
        self.cells: List[Optional[TernaryCell]] = [None] * (width * height)
        self._next_id: int = 0

    def place(self, x: int, y: int, value: int) -> bool:
        """Place a cell at position (x, y). Returns False if out of bounds."""
        if x >= self.width or y >= self.height:
            return False
        cell = TernaryCell(id=self._next_id, ternary_value=value)
        self._next_id += 1
        self.cells[y * self.width + x] = cell
        return True

    def get(self, x: int, y: int) -> Optional[TernaryCell]:
        if x >= self.width or y >= self.height:
            return None
        return self.cells[y * self.width + x]

    def neighbors(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get 4-connected neighbor positions."""
        result: List[Tuple[int, int]] = []
        if x > 0:
            result.append((x - 1, y))
        if x + 1 < self.width:
            result.append((x + 1, y))
        if y > 0:
            result.append((x, y - 1))
        if y + 1 < self.height:
            result.append((x, y + 1))
        return result

    def propagate_signals(self) -> None:
        """Collect emissions from all cells and deliver to neighbors."""
        emissions: List[Tuple[int, int, TernaryMessenger]] = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.get(x, y)
                if cell is not None and cell.is_alive():
                    emissions.append((x, y, cell.emit()))

        for x, y, msg in emissions:
            for nx, ny in self.neighbors(x, y):
                neighbor = self.get(nx, ny)
                if neighbor is not None:
                    neighbor.receive(msg)

    def tick_all(self) -> int:
        """Run one tick across all cells. Returns alive count."""
        self.propagate_signals()
        alive = 0
        for cell in self.cells:
            if cell is not None and cell.is_alive():
                cell.tick()
                alive += 1
        # Remove apoptotic cells
        for i, cell in enumerate(self.cells):
            if cell is not None and not cell.is_alive():
                self.cells[i] = None
        return alive

    def alive_count(self) -> int:
        return sum(1 for c in self.cells if c is not None and c.is_alive())

    def tissue_balance(self) -> Tuple[int, int, int]:
        """Returns (positive, zero, negative) counts of alive cells."""
        pos = zero = neg = 0
        for cell in self.cells:
            if cell is not None and cell.is_alive():
                if cell.ternary_value == 1:
                    pos += 1
                elif cell.ternary_value == 0:
                    zero += 1
                elif cell.ternary_value == -1:
                    neg += 1
        return pos, zero, neg


class Tissue:
    """Tissue coordinator for grid-level operations."""

    def __init__(self, width: int, height: int) -> None:
        self.grid: CellGrid = CellGrid(width, height)

    def fill_pattern(self, pattern: List[int]) -> None:
        """Fill grid with a flat pattern (row-major)."""
        for i, val in enumerate(pattern):
            x = i % self.grid.width
            y = i // self.grid.width
            self.grid.place(x, y, val)

    def run(self, ticks: int) -> int:
        """Run tissue for N ticks. Returns alive count."""
        for _ in range(ticks):
            self.grid.tick_all()
        return self.grid.alive_count()

    def is_converged(self) -> bool:
        """Check if all alive cells have the same ternary value."""
        values: Set[int] = set()
        for cell in self.grid.cells:
            if cell is not None and cell.is_alive():
                values.add(cell.ternary_value)
        return len(values) <= 1

    def consensus(self) -> int:
        """Compute tissue-level consensus ternary value."""
        pos, zero, neg = self.grid.tissue_balance()
        if pos > zero and pos > neg:
            return 1
        elif neg > pos and neg > zero:
            return -1
        return 0
