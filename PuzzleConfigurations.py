from typing import List, Tuple
from itertools import permutations
from enum import Enum

class GroupToCheck(Enum):
    ROW = "Row"
    COLUMN = "Column"

def possible_configurations(puzzle: List[List[int]], group: GroupToCheck) -> List[Tuple[List[Tuple[int, int]], List[List[int]]]]:
    if len(puzzle) != 4 or any(len(row) != 4 for row in puzzle):
        raise ValueError("Expected a 4x4 puzzle!")

    result: List[Tuple[List[Tuple[int, int]], List[List[int]]]] = []

    for group_index in range(4):
        if group == GroupToCheck.ROW:
            current_group = puzzle[group_index]
        else:
            current_group = [puzzle[r][group_index] for r in range(4)]

        empty_cells: List[Tuple[int, int]] = [
            (group_index, i) if group == GroupToCheck.ROW else (i, group_index)
            for i, val in enumerate(current_group) if val == 0
        ]

        non_zero = [val for val in current_group if val != 0]
        missing = [v for v in range(1, 5) if v not in non_zero]
        permutations_of_missing = permutations(missing)
        result.append((empty_cells, permutations_of_missing))

    return result


def row_possible_values(puzzle: List[List[int]]) -> List[Tuple[List[Tuple[int, int]], List[List[int]]]]:
    return possible_configurations(puzzle, GroupToCheck.ROW)

def column_possible_values(puzzle: List[List[int]]) -> List[Tuple[List[Tuple[int, int]], List[List[int]]]]:
    return possible_configurations(puzzle, GroupToCheck.COLUMN)

def square_possible_values(puzzle: List[List[int]]) -> List[Tuple[List[Tuple[int, int]], List[List[int]]]]:
    if len(puzzle) != 4 or any(len(row) != 4 for row in puzzle):
        raise ValueError("Expected a 4x4 puzzle!")

    result: List[Tuple[List[Tuple[int, int]], List[List[int]]]] = []

    for square_row_index in range(2):
        for square_col_index in range(2):
            current_square_indices = [
                (r, c)
                for r in range(2 * square_row_index, 2 * square_row_index + 2)
                for c in range(2 * square_col_index, 2 * square_col_index + 2)
            ]

            empty_cells = [(r, c) for (r, c) in current_square_indices if puzzle[r][c] == 0]

            current_square_values = [
                puzzle[r][c] for (r, c) in current_square_indices if puzzle[r][c] != 0
            ]

            missing_values = [v for v in range(1, 5) if v not in current_square_values]

            result.append((empty_cells, permutations(missing_values)))

    return result


def complete_trivial_missing_values(puzzle: List[List[int]], group: GroupToCheck) -> int:
    if len(puzzle) != 4 or any(len(row) != 4 for row in puzzle):
        raise ValueError("Expected a 4x4 puzzle!")

    number_of_changes = 0

    for group_index in range(4):
        if group == GroupToCheck.ROW:
            current_group = puzzle[group_index]
        else:
            current_group = [puzzle[r][group_index] for r in range(4)]

        empty_indices = [i for i, val in enumerate(current_group) if val == 0]

        if len(empty_indices) == 1:
            non_zero = [val for val in current_group if val != 0]
            missing = [v for v in range(1, 5) if v not in non_zero]
            element_index = empty_indices[0]
            missing_value = missing[0]

            if group == GroupToCheck.ROW:
                puzzle[group_index][element_index] = missing_value
            else:
                puzzle[element_index][group_index] = missing_value

            number_of_changes += 1

    return number_of_changes

def complete_trivial_missing_square_values(puzzle: List[List[int]]) -> int:
    number_of_changes = 0

    if len(puzzle) != 4 or any(len(row) != 4 for row in puzzle):
        raise ValueError("Expected a 4x4 puzzle!")

    for square_row_index in range(2):
        for square_col_index in range(2):
            current_square_indices = [
                (r, c)
                for r in range(2 * square_row_index, 2 * square_row_index + 2)
                for c in range(2 * square_col_index, 2 * square_col_index + 2)
            ]

            empty_cells = [
                (r, c) for (r, c) in current_square_indices if puzzle[r][c] == 0
            ]

            if len(empty_cells) == 1:
                current_square_values = [
                    puzzle[r][c]
                    for (r, c) in current_square_indices
                    if puzzle[r][c] != 0
                ]

                missing_values = [v for v in range(1, 5) if v not in current_square_values]
                r, c = empty_cells[0]
                puzzle[r][c] = missing_values[0]
                number_of_changes += 1

    return number_of_changes



def main() -> None:
    puzzle: List[List[int]] = [
        [3, 1, 4, 2],
        [2, 0, 0, 1],
        [1, 0, 0, 0],
        [4, 0, 0, 3]
    ]

    print("Started with the following puzzle:")
    print(puzzle)

    changes = 0
    while True:
        changes = complete_trivial_missing_values(puzzle, GroupToCheck.ROW)
        changes += complete_trivial_missing_values(puzzle, GroupToCheck.COLUMN)
        changes += complete_trivial_missing_square_values(puzzle)
        if changes == 0:
            break

    print("Completed trivial missing values. Current puzzle:")
    print(puzzle)
    
    for row_index, (cell_positions, possible_configurations) in enumerate(row_possible_values(puzzle)):
        cells_str = ", ".join(str((r,c)) for r, c in cell_positions)
        configs_str = ", ".join(str(config) for config in possible_configurations)
        print(f"Row {row_index}: empty cells: {{{cells_str}}}; possible configurations: {{{configs_str}}}")

    for column_index, (cell_positions, possible_configurations) in enumerate(column_possible_values(puzzle)):
        cells_str = ", ".join(str((r,c)) for r, c in cell_positions)
        configs_str = ", ".join(str(config) for config in possible_configurations)
        print(f"Column {column_index}: empty cells: {{{cells_str}}}; possible configurations: {{{configs_str}}}")

    for square_index, (cell_positions, possible_configurations) in enumerate(square_possible_values(puzzle)):
        cells_str = ", ".join(str((r,c)) for r, c in cell_positions)
        configs_str = ", ".join(str(config) for config in possible_configurations)
        print(f"Square {square_index}: empty cells: {{{cells_str}}}; possible configurations: {{{configs_str}}}")

if __name__ == "__main__":
    main()
