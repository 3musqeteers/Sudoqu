# Sudoqu
2x2 Sudoku solver in Qiskit!

## Usage
```python
from SudoquSolver import solve_sudoqu

puzzle: List[List[int]] = [
    [3, 1, 4, 2],
    [2, 0, 0, 1],
    [1, 0, 0, 0],
    [4, 0, 0, 3]
]

print("Started with the following puzzle:")
for row in puzzle:
    print(row)
print()

solution = solve_sudoqu(puzzle)

print("Solution with highest probability:")
for row in solution:
    print(row)
print()
```

## Implementation
The implementation first fills the trivial missing cells and then creates a quantum circuit and utilizes Grover's algorithm.  In short, we translate a given problem into maximum twelve sets of constraints (corresponding to individual rows, columns, and squares) then attempt to find the configuration satisfying all of them using Grover's algorithm.

## Notebook
See [solver.ipynb](https://github.com/3musqeteers/Sudoqu/blob/main/solver.ipynb) which outlines the Sudoku solver with step-by-step explanations.