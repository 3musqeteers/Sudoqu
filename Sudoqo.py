from typing import List, Tuple, Dict

def puzzle_indices(n_squared: int) -> List[Tuple[int, int]]:
    """Generate all (i, j) indices for an n_squared x n_squared grid."""
    result: List[Tuple[int, int]] = []
    for i in range(n_squared):
        for j in range(n_squared):
            result.append((i, j))
    return result

def indices_of_non_equal_elements(n: int) -> List[Tuple[int, int]]:
    """
    Generate pairs of indices that must have non-equal elements in a Sudoku-like puzzle.
    Returns a list of tuples where each tuple contains two indices that cannot have the same value.
    """
    result: List[Tuple[int, int]] = []
    n_squared: int = n * n
    indices: List[Tuple[int, int]] = puzzle_indices(n_squared)
    
    # Create a dictionary mapping position tuples to their index in the list
    position_to_index: Dict[Tuple[int, int], int] = {pos: i for i, pos in enumerate(indices)}

    for index in range(n_squared):
        i: int
        j: int
        i, j = indices[index]
        
        # Get all indices in the same row
        row_indices: List[Tuple[int, int]] = [(i, column) for column in range(n_squared)]
        print(row_indices)

        # Get all indices in the same column
        column_indices: List[Tuple[int, int]] = [(row, j) for row in range(n_squared)]
        print(column_indices)
        
        # Get all indices in the same n x n square
        current_square_row: int = n * (i // n)
        current_square_column: int = n * (j // n)
        square_indices: List[Tuple[int, int]] = [
            (row, column)
            for row in range(current_square_row, current_square_row + n)
            for column in range(current_square_column, current_square_column + n)
        ]
        print(square_indices)
        

        # Combine all indices (using set to remove duplicates, then convert back to list)
        all_indices: List[Tuple[int, int]] = list(set(position_to_index[position] for position in row_indices + column_indices + square_indices))
        print(all_indices)

        # Add pairs where the other index is greater than current index
        for current_index in all_indices:
            if current_index > index:
                result.append((index, current_index))
    
    return result

# Example usage:
if __name__ == "__main__":
    print(indices_of_non_equal_elements(2))