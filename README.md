# ternary-cell-python

Faithful Python port of [ternary-cell](https://github.com/SuperInstance/ternary-cell) — cellular computing with ternary tick cycles.

## What

`TernaryCell` implements a six-phase lifecycle: `predict → perceive → surprise → vibe → gc → conservation`. Each cell carries energy, a ternary value (-1/0/+1), a prediction, surprise accumulation, and an inbox of `TernaryMessenger` signals. `CellGrid` arranges cells in a 2D grid with 4-connected neighbor signaling. `Tissue` coordinates grid-level operations.

Pure Python, zero dependencies.

## Install

```bash
pip install -e .
```

## Usage

```python
from ternary_cell import TernaryCell, TernaryMessenger, CellGrid, Tissue

# Single cell
cell = TernaryCell(id=0)
cell.receive(TernaryMessenger.SIGNAL)
cell.tick()
print(cell.ternary_value)  # 1

# Grid
tissue = Tissue(3, 3)
tissue.fill_pattern([1, 0, -1, 0, 1, 0, -1, 0, 1])
alive = tissue.run(10)
print(f"Alive: {alive}, Consensus: {tissue.consensus()}, Converged: {tissue.is_converged()}")
```

## Test

```bash
pytest tests/ -v
```

## Architecture

Matches the Rust `ternary-cell` 1:1:

- `TernaryMessenger` — Signal / Silence / Suppress ({+1, 0, -1})
- `TernaryCell` — 6-phase tick, energy, division, apoptosis
- `CellGrid` — 2D grid, 4-connected neighbors, signal propagation
- `Tissue` — grid-level run/converge/consensus

## License

MIT
