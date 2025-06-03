# Sudoqu
Sudoku solver in Qiskit!
* **PuzzleConfigurations.py** contains constraint-checker helper functions.
* **solver.ipynb** outlines the Sudoku solver with step-by-step explanations. In short, we translate a given problem into maximum twelve sets of constraints (corresponding to individual rows, columns, and squares) then attempt to find the configuration satisfying all of them using Grover's algorithm.
