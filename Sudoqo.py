import math
from typing import List, Tuple, Dict

def constraints(puzzle: List[List[int]]) -> Tuple[List[Tuple[int, int]], Dict[int, List[int]], Dict[int, List[int]]]:
    """
    Generate constraints for a Sudoku puzzle.
    
    Args:
        puzzle: 2D list representing the Sudoku puzzle (0 for empty cells)
    
    Returns:
        Tuple containing:
        - indices: List of (row, col) positions of empty cells
        - index_constraints: Dict mapping each empty cell index to indices of other empty cells in same row/col/square
        - constant_constraints: Dict mapping each empty cell index to known values in same row/col/square
    """
    for index in range(len(puzzle)):
        if len(puzzle) != len(puzzle[index]):
            raise ValueError("Expected a square puzzle!")

    n_squared = len(puzzle)
    n = int(math.sqrt(n_squared))
    
    if n * n != n_squared:
        raise ValueError("Expected a square puzzle of square size!")
    
    indices = get_indices_of_empty_values(puzzle, n_squared)
    position_to_index = {pos: i for i, pos in enumerate(indices)}
    
    constant_constraints = {}
    index_constraints = {}
    
    for index in range(len(indices)):
        i, j = indices[index]
        
        # Get all positions in the same row
        row_indices = [(i, col) for col in range(n_squared)]
        
        # Get all positions in the same column
        column_indices = [(row, j) for row in range(n_squared)]
        
        # Get all positions in the same n×n square
        current_square_row = n * (i // n)
        current_square_column = n * (j // n)
        square_indices = [
            (row, col) 
            for row in range(current_square_row, current_square_row + n)
            for col in range(current_square_column, current_square_column + n)
        ]
        
        # Combine all constraint positions (remove duplicates using set)
        all_indices = list(set(row_indices + column_indices + square_indices))
        
        # Get constant constraints (non-zero values in same row/col/square)
        constant_constraints[index] = list(set([
            puzzle[pos[0]][pos[1]] 
            for pos in all_indices 
            if puzzle[pos[0]][pos[1]] != 0
        ]))
        
        # Get index constraints (indices of other empty cells in same row/col/square)
        index_constraints[index] = [
            position_to_index[pos] 
            for pos in all_indices 
            if puzzle[pos[0]][pos[1]] == 0 and position_to_index[pos] != index
        ]
    
    return indices, index_constraints, constant_constraints


def get_indices_of_empty_values(puzzle: List[List[int]], n_squared: int) -> List[Tuple[int, int]]:
    """
    Get the indices of all empty (zero) values in the puzzle.
    
    Args:
        puzzle: 2D list representing the puzzle
        n_squared: Size of the puzzle (number of rows/columns)
    
    Returns:
        List of (row, col) tuples for empty positions
    """
    result = []
    for i in range(n_squared):
        for j in range(n_squared):
            if puzzle[i][j] == 0:
                result.append((i, j))
    return result


# Example usage:
if __name__ == "__main__":
    # Example 4x4 Sudoku puzzle (0 represents empty cells)
    sample_puzzle = [
        [1, 0, 0, 4],
        [0, 2, 0, 0],
        [0, 0, 3, 0],
        [4, 0, 0, 1]
    ]
    
    indices, index_constraints, constant_constraints = constraints(sample_puzzle)
    
    print("Empty cell positions:", indices)
    print("Index constraints:", index_constraints)
    print("Constant constraints:", constant_constraints)