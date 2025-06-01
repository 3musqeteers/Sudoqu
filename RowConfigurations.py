from itertools import permutations
from typing import List, Tuple

def row_possible_values(puzzle: List[List[int]]) -> List[Tuple[List[Tuple[int, int]], List[List[int]]]]:
    if len(puzzle) != 4 or any(len(row) != 4 for row in puzzle):
        raise ValueError("Expected a 4x4 puzzle!")

    result: List[Tuple[List[Tuple[int, int]], List[List[int]]]] = []

    for row_index, row in enumerate(puzzle):
        empty_cells: List[Tuple[int, int]] = [
            (row_index, i) for i, val in enumerate(row) if val == 0
        ]
        non_zero_values: List[int] = [val for val in row if val != 0]
        missing_values: List[int] = [v for v in range(1, 5) if v not in non_zero_values]
        possible_configurations: List[List[int]] = [list(p) for p in permutations(missing_values)]
        result.append((empty_cells, possible_configurations))

    return result

def main() -> None:
    puzzle: List[List[int]] = [
        [3, 1, 4, 2],
        [2, 0, 0, 1],
        [1, 0, 0, 0],
        [4, 0, 0, 3]
    ]

    row_info: List[Tuple[List[Tuple[int, int]], List[List[int]]]] = row_possible_values(puzzle)

    for i, (cell_positions, possible_configurations) in enumerate(row_info):
        cells_str = ", ".join(f"({r}, {c})" for r, c in cell_positions)
        configs_str = ", ".join(str(config) for config in possible_configurations)
        print(f"Row {i}: empty cells: {{{cells_str}}}; possible configurations: {{{configs_str}}}")

if __name__ == "__main__":
    main()
