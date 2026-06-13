# Ternary Cell (Python)

A **ternary cell** is the fundamental computational unit in balanced ternary logic — a cell that holds one of three states: **Negative (−1)**, **Neutral (0)**, or **Positive (+1)**. This Python package implements ternary cell grids with formula evaluation, providing the building blocks for ternary spreadsheet computation and ternary strategy simulation.

## Why It Matters

Binary logic (0 and 1) is the foundation of digital computing, but balanced ternary (−1, 0, +1) offers several theoretical advantages: ternary numbers are more compact (log₂(3) ≈ 1.585 bits per trit), balanced ternary arithmetic simplifies sign handling (no separate sign bit), and three-valued logic naturally represents unknown/neutral states that binary requires hacky workarounds for. The ternary cell is the atomic unit — analogous to a bit in binary systems — and composing grids of ternary cells enables ternary spreadsheet computation, strategy simulation, and the study of emergent ternary dynamics that are central to the SuperInstance framework.

## How It Works

### Balanced Ternary Arithmetic

Each cell holds a value from {−1, 0, +1}. The elementary operations differ from binary:

| Operation | Truth Table | Notation |
|-----------|-------------|----------|
| Negation | −(−1)=+1, −0=0, −(+1)=−1 | ā |
| Min (AND-like) | min(a, b) | a∧b |
| Max (OR-like) | max(a, b) | a∨b |
| Consensus | −1 if both = −1, +1 if both = +1, else 0 | a⊙b |
| Sum (truncated) | a+b clamped to [−1, +1] | a⊕b |

### Ternary Grid

A grid of N×M ternary cells supports:
- **Direct values**: set cell(r,c) = −1, 0, or +1
- **Formulas**: SUM, PRODUCT, THRESHOLD over rectangular ranges
- **Evaluation**: topological sort for dependency resolution

Formula evaluation uses clamped ternary arithmetic:
```
SUM(a, b, c) = clamp(a + b + c, -1, +1)
THRESHOLD(range, t) = +1 if Σ > t, −1 if Σ < −t, else 0
```

### Complexity

| Operation | Time | Space |
|-----------|------|-------|
| Cell access | O(1) | O(1) |
| Formula eval (k×k range) | O(k²) | O(k²) |
| Grid evaluate (all formulas) | O(N·M + E) | O(N·M) |

where E = total formula dependencies across the grid.

## Quick Start

```python
from ternary_cell import TernaryCell, TernaryValue

cell = TernaryCell(TernaryValue.POSITIVE)
print(cell.value)  # +1

# Negate
cell_neg = -cell
print(cell_neg.value)  # -1

# Consensus
neutral = TernaryCell(TernaryValue.NEUTRAL)
result = cell.consensus(cell_neg)
print(result.value)  # 0 (positive and negative cancel)
```

## API

| Class | Methods | Description |
|-------|---------|-------------|
| `TernaryCell` | `value`, `negate()`, `consensus()` | Single ternary value holder |
| `TernaryValue` | `NEGATIVE`, `NEUTRAL`, `POSITIVE` | Enum of ternary states |
| `TernaryGrid` | `get()`, `set()`, `evaluate()` | N×M grid with formula support |

## Architecture Notes

The ternary cell is the atomic primitive of the γ + η = C framework. The three values map directly: **+1 = γ** (constructive, chosen, present), **−1 = η** (avoidant, rejected, absent), **0 = neutral** (undecided, unknown, transitional). A grid of ternary cells computes the dynamics of γ and η interaction over space and time, producing emergent competence C. This is the discrete computational substrate on which all SuperInstance ternary experiments run. See [ARCHITECTURE.md](https://github.com/SuperInstance/SuperInstance/blob/main/ARCHITECTURE.md).

## References

1. Knuth, D. E. (1981). *The Art of Computer Programming, Vol. 2: Seminumerical Algorithms*, 2nd ed. Addison-Wesley. — Section 4.1 on balanced ternary number systems.
2. Frieder, G., & Luk, C. (1975). "Ternary Computers." In *Proceedings of the IEEE*. — Survey of ternary computing hardware.
3. Hayes, B. (2001). "Third Base." *American Scientist*, 89(6), 490–494. — Popular introduction to balanced ternary.

## License

MIT
