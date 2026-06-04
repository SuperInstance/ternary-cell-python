"""Tests for ternary-cell-python — 20+ tests covering the full Rust port."""

import pytest
from ternary_cell import (
    CellGrid,
    CellState,
    TernaryCell,
    TernaryMessenger,
    Tissue,
)


# ---------------------------------------------------------------------------
# TernaryMessenger
# ---------------------------------------------------------------------------


class TestTernaryMessenger:
    def test_roundtrip(self):
        for v in [-1, 0, 1]:
            assert TernaryMessenger.from_ternary(v).to_ternary() == v

    def test_invalid_ternary(self):
        assert TernaryMessenger.from_ternary(2) is None
        assert TernaryMessenger.from_ternary(-5) is None

    def test_combine_max_wins(self):
        a = TernaryMessenger.combine(TernaryMessenger.SIGNAL, TernaryMessenger.SUPPRESS)
        assert a == TernaryMessenger.SIGNAL

        b = TernaryMessenger.combine(TernaryMessenger.SILENCE, TernaryMessenger.SUPPRESS)
        assert b == TernaryMessenger.SILENCE

    def test_combine_equal(self):
        c = TernaryMessenger.combine(TernaryMessenger.SUPPRESS, TernaryMessenger.SUPPRESS)
        assert c == TernaryMessenger.SUPPRESS


# ---------------------------------------------------------------------------
# TernaryCell — basics
# ---------------------------------------------------------------------------


class TestTernaryCell:
    def test_new_defaults(self):
        cell = TernaryCell(id=0)
        assert cell.ternary_value == 0
        assert cell.energy == 10
        assert cell.state == CellState.ACTIVE
        assert cell.is_alive()

    def test_with_value_clamps(self):
        c1 = TernaryCell(id=0, ternary_value=5)
        assert c1.ternary_value == 1
        c2 = TernaryCell(id=1, ternary_value=-3)
        assert c2.ternary_value == -1

    def test_tick_basic(self):
        cell = TernaryCell(id=0)
        surprise = cell.tick()
        assert surprise == 0  # no signals, no change
        assert cell.tick_count == 1

    def test_receive_and_tick(self):
        cell = TernaryCell(id=0)
        cell.receive(TernaryMessenger.SIGNAL)
        cell.receive(TernaryMessenger.SIGNAL)
        cell.tick()
        assert cell.ternary_value == 1

    def test_tick_with_surprise(self):
        cell = TernaryCell(id=0, ternary_value=1)
        cell.receive(TernaryMessenger.SUPPRESS)
        cell.tick()
        # predict: combined=-1 → prediction=-1
        # perceive: combined=-1 → ternary_value=-1
        # surprise = |-1 - (-1)| = 0
        assert cell.surprise == 0

    def test_emit(self):
        cell = TernaryCell(id=0, ternary_value=1)
        assert cell.emit() == TernaryMessenger.SIGNAL

        cell2 = TernaryCell(id=1, ternary_value=-1)
        assert cell2.emit() == TernaryMessenger.SUPPRESS

        cell3 = TernaryCell(id=2, ternary_value=0)
        assert cell3.emit() == TernaryMessenger.SILENCE


# ---------------------------------------------------------------------------
# TernaryCell — lifecycle
# ---------------------------------------------------------------------------


class TestCellLifecycle:
    def test_divide(self):
        cell = TernaryCell(id=0, ternary_value=1)
        daughter = cell.divide(daughter_id=1)
        assert daughter is not None
        assert daughter.generation == 1
        assert daughter.ternary_value == 1
        assert cell.energy == 5
        assert cell.state == CellState.DIVIDING

    def test_cannot_divide_low_energy(self):
        cell = TernaryCell(id=0, energy=3)
        assert cell.divide(daughter_id=1) is None

    def test_cannot_divide_not_active(self):
        cell = TernaryCell(id=0, energy=10)
        cell.state = CellState.DIVIDING
        assert cell.divide(daughter_id=1) is None

    def test_apoptosis(self):
        cell = TernaryCell(id=0, energy=1)
        cell.receive(TernaryMessenger.SIGNAL)
        cell.predict()
        cell.ternary_value = -1  # force mismatch
        s = cell.compute_surprise()
        assert s == 2
        cell.vibe()
        assert cell.energy == -1
        cell.gc()
        cell.conservation()
        assert cell.state == CellState.APOPTOTIC
        assert not cell.is_alive()

    def test_energy_clamped(self):
        cell = TernaryCell(id=0, energy=25)
        cell.conservation()
        assert cell.energy == 20


# ---------------------------------------------------------------------------
# CellGrid
# ---------------------------------------------------------------------------


class TestCellGrid:
    def test_place_and_get(self):
        grid = CellGrid(3, 3)
        assert grid.place(1, 1, 1)
        cell = grid.get(1, 1)
        assert cell is not None
        assert cell.ternary_value == 1

    def test_place_out_of_bounds(self):
        grid = CellGrid(2, 2)
        assert not grid.place(5, 5, 1)

    def test_get_out_of_bounds(self):
        grid = CellGrid(2, 2)
        assert grid.get(5, 5) is None

    def test_neighbors_center(self):
        grid = CellGrid(3, 3)
        n = grid.neighbors(1, 1)
        assert len(n) == 4
        assert set(n) == {(0, 1), (2, 1), (1, 0), (1, 2)}

    def test_neighbors_corner(self):
        grid = CellGrid(3, 3)
        n = grid.neighbors(0, 0)
        assert len(n) == 2
        assert set(n) == {(1, 0), (0, 1)}

    def test_tick_all(self):
        grid = CellGrid(2, 2)
        grid.place(0, 0, 1)
        grid.place(1, 0, 1)
        grid.place(0, 1, -1)
        grid.place(1, 1, -1)
        alive = grid.tick_all()
        assert alive == 4

    def test_alive_count(self):
        grid = CellGrid(2, 2)
        grid.place(0, 0, 1)
        grid.place(1, 0, 0)
        assert grid.alive_count() == 2

    def test_tissue_balance(self):
        grid = CellGrid(2, 2)
        grid.place(0, 0, 1)
        grid.place(1, 0, 0)
        grid.place(0, 1, -1)
        grid.place(1, 1, 1)
        pos, zero, neg = grid.tissue_balance()
        assert pos == 2
        assert zero == 1
        assert neg == 1


# ---------------------------------------------------------------------------
# Tissue
# ---------------------------------------------------------------------------


class TestTissue:
    def test_fill_pattern(self):
        tissue = Tissue(2, 2)
        tissue.fill_pattern([1, -1, 0, 1])
        assert tissue.grid.get(0, 0).ternary_value == 1
        assert tissue.grid.get(1, 0).ternary_value == -1

    def test_converged(self):
        tissue = Tissue(2, 2)
        tissue.fill_pattern([1, 1, 1, 1])
        assert tissue.is_converged()

    def test_not_converged(self):
        tissue = Tissue(2, 2)
        tissue.fill_pattern([1, -1, 1, -1])
        assert not tissue.is_converged()

    def test_consensus(self):
        tissue = Tissue(3, 1)
        tissue.fill_pattern([1, 1, -1])
        assert tissue.consensus() == 1

    def test_consensus_tie(self):
        tissue = Tissue(2, 1)
        tissue.fill_pattern([1, -1])
        assert tissue.consensus() == 0

    def test_run(self):
        tissue = Tissue(2, 2)
        tissue.fill_pattern([1, 0, -1, 0])
        alive = tissue.run(3)
        assert alive <= 4

    def test_run_many_ticks(self):
        """After many ticks, a homogeneous grid stays alive."""
        tissue = Tissue(3, 3)
        tissue.fill_pattern([1] * 9)
        alive = tissue.run(50)
        assert alive == 9  # all agree, no surprise, no death


# ---------------------------------------------------------------------------
# Cross-cutting
# ---------------------------------------------------------------------------


class TestCrossCutting:
    def test_signal_propagation_changes_values(self):
        """A majority of positive neighbors should flip a negative cell."""
        grid = CellGrid(3, 1)
        grid.place(0, 0, 1)
        grid.place(1, 0, -1)
        grid.place(2, 0, 1)
        # Before: [1, -1, 1]
        grid.tick_all()
        # Middle cell receives Signal from both sides → should flip to 1
        middle = grid.get(1, 0)
        assert middle is not None
        assert middle.ternary_value == 1

    def test_division_doubles_population(self):
        """Cells with enough energy can divide."""
        cell = TernaryCell(id=0, ternary_value=1, energy=10)
        daughter = cell.divide(daughter_id=1)
        assert daughter is not None
        assert cell.energy == 5
        assert daughter.energy == 5

    def test_inbox_cleared_after_tick(self):
        cell = TernaryCell(id=0)
        cell.receive(TernaryMessenger.SIGNAL)
        cell.receive(TernaryMessenger.SUPPRESS)
        assert len(cell.inbox) == 2
        cell.tick()
        assert len(cell.inbox) == 0

    def test_multiple_ticks_accumulate(self):
        cell = TernaryCell(id=0)
        for _ in range(5):
            cell.receive(TernaryMessenger.SIGNAL)
            cell.tick()
        assert cell.tick_count == 5
        assert cell.ternary_value == 1
