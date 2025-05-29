import math
from typing import List, Tuple, Dict
from qiskit import QuantumRegister, QuantumCircuit

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

        # Get all indices in the same column
        column_indices: List[Tuple[int, int]] = [(row, j) for row in range(n_squared)]
        
        # Get all indices in the same n x n square
        current_square_row: int = n * (i // n)
        current_square_column: int = n * (j // n)
        square_indices: List[Tuple[int, int]] = [
            (row, column)
            for row in range(current_square_row, current_square_row + n)
            for column in range(current_square_column, current_square_column + n)
        ]        

        # Combine all indices (using set to remove duplicates, then convert back to list)
        all_indices: List[Tuple[int, int]] = list(set(position_to_index[position] for position in row_indices + column_indices + square_indices))

        # Add pairs where the other index is greater than current index
        for current_index in all_indices:
            if current_index > index:
                result.append((index, current_index))
    
    return result

def initialize_registers(puzzle: List[List[int]]) -> List[QuantumRegister]:
    registers = []
    n_squared = len(puzzle)
    
    # Check if all rows have the same length as the number of rows (square matrix)
    if not all(len(row) == n_squared for row in puzzle):
        raise ValueError("Expected a square matrix!")
    
    n = int(math.sqrt(n_squared))
    if n * n != n_squared:
        raise ValueError("Expected a square matrix of square size!")
    
    number_of_bits = math.log(n, 2) + 1
    if number_of_bits != int(number_of_bits):
        raise ValueError("Expected a square matrix of size equal to a power of 4!")
    
    number_of_bits_integer = int(number_of_bits)
    index = 0
    for i in range(n_squared):
        for j in range(n_squared):
            register_name = f'q{index}: (cell {(i,j)})'
            registers.append(QuantumRegister(size =  number_of_bits_integer, name = register_name))
            index += 1

    index = 0

    qc = QuantumCircuit(*registers)
    for i in range(n_squared):
        for j in range(n_squared):
            current_value = puzzle[i][j]
            if current_value != 0:
                current_binary_value = to_binary(current_value, number_of_bits_integer)
                initialize_register(qc, registers[index], current_binary_value)
            index += 1

    return (qc,registers)

def initialize_register(qc: QuantumCircuit, register: QuantumRegister, binary_value: List[int]):
    index : int = 0
    for current in binary_value:
        if (current == 1):
            qc.x(register[index])
            qc.barrier()
        index = index + 1

def to_binary(number: int, number_of_bits: int) -> List[int]:
    result = []
    for i in range(number_of_bits):
        result.append(number % 2)
        number //= 2
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
    
    qc, registers = initialize_registers(sample_puzzle)
    print(qc)