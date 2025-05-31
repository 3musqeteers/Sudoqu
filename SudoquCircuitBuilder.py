import math
from typing import List, Tuple, Dict
from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

def build_sudoku_circuit(puzzle: List[List[int]]) -> QuantumCircuit:
    (empty_cells, index_constaints, constant_constraints) = constraints(puzzle)
    builder = QuantumConstraintCircuitBuilder()
    for i in range(len(empty_cells)):
        current_name = str(empty_cells[i])
        builder.define(str(empty_cells[i]))
        for current_constant in constant_constraints[i]:
            builder.not_equal_constant(current_name, current_constant-1)

    for i in range(len(empty_cells)):
        for current_index_constraint in index_constaints[i]:
            current_name = str(empty_cells[i])
            builder.not_equal(current_name, str(empty_cells[current_index_constraint]))
    
    return builder.build_circuit(2, True)
        

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

from qiskit import QuantumCircuit, QuantumRegister, AncillaRegister

class QuantumConstraintCircuitBuilder:
    def __init__(self):
        self.variables = []
        self.not_equal_constraints = []
        self.not_equal_constant_constraints = []
    
    def define(self, name: str):
        if name in [v["name"] for v in self.variables]:
            raise ValueError(f"Variable {name} already defined.")
        self.variables.append({"name": name, "register": None})
    
    def not_equal(self, name1: str, name2: str):
        self.not_equal_constraints.append((name1, name2))
    
    def not_equal_constant(self, name: str, value: int):
        self.not_equal_constant_constraints.append((name, value))
    
    def build_circuit(self, num_qubits_per_var: int, reversible_with_phase: bool = False) -> QuantumCircuit:
        var_regs = {}
        
        # Quantum registers for variables
        for var in self.variables:
            qreg = QuantumRegister(num_qubits_per_var, name=var["name"])
            var["register"] = qreg
            var_regs[var["name"]] = qreg
        
        # Constant qubits: |0> and |1>
        const_zero = QuantumRegister(1, name='const0')
        const_one = QuantumRegister(1, name='const1')
        
        # Optimized ancilla calculation - reuse ancillas across constraints
        # We need:
        # - num_qubits_per_var for comparison bits (reusable)
        # - 1 final flag bit per constraint (must persist for phase marking)
        # - max(0, num_qubits_per_var - 2) for multi-controlled gates (reusable)
        total_constraints = len(self.not_equal_constraints) + len(self.not_equal_constant_constraints)
        
        comparison_ancillas = num_qubits_per_var  # Reused for each constraint
        multi_control_ancillas = max(0, num_qubits_per_var - 2)  # Reused for each constraint
        flag_ancillas = total_constraints  # One per constraint, persistent
        
        total_ancillas = comparison_ancillas + multi_control_ancillas + flag_ancillas
        ancilla = AncillaRegister(total_ancillas, name='anc')
        
        qc = QuantumCircuit(*(v["register"] for v in self.variables), const_zero, const_one, ancilla)
        
        # Initialize const_one to |1>
        qc.x(const_one)
        
        # Ancilla allocation strategy:
        # [0:num_qubits_per_var] - comparison bits (reusable)
        # [num_qubits_per_var:num_qubits_per_var + multi_control_ancillas] - multi-control temp bits (reusable)  
        # [num_qubits_per_var + multi_control_ancillas:] - flag bits (one per constraint, persistent)
        
        comp_start = 0
        multi_control_start = num_qubits_per_var
        flag_start = num_qubits_per_var + multi_control_ancillas
        
        operations = []  # List of lambdas to reverse operations
        constraint_idx = 0
        
        # Constraint: not_equal(variable, variable)
        for name1, name2 in self.not_equal_constraints:
            reg1 = var_regs[name1]
            reg2 = var_regs[name2]
            comp_bits = [ancilla[comp_start + i] for i in range(num_qubits_per_var)]
            final_flag = ancilla[flag_start + constraint_idx]
            multi_control_bits = [ancilla[multi_control_start + i] for i in range(multi_control_ancillas)]
            
            # XOR comparison (reusing comparison ancillas)
            for i in range(num_qubits_per_var):
                qc.cx(reg1[i], comp_bits[i])
                operations.append(lambda r1=reg1[i], c=comp_bits[i]: qc.cx(r1, c))
                qc.cx(reg2[i], comp_bits[i])
                operations.append(lambda r2=reg2[i], c=comp_bits[i]: qc.cx(r2, c))
            
            # Inequality logic (reusing multi-control ancillas)
            ops = self._add_inequality_logic(qc, comp_bits, final_flag, multi_control_bits, num_qubits_per_var)
            operations.extend(ops)
            
            constraint_idx += 1
        
        # Constraint: not_equal(variable, constant)
        for name, const in self.not_equal_constant_constraints:
            reg = var_regs[name]
            const_bits = list(bin(const)[2:].zfill(num_qubits_per_var))[-num_qubits_per_var:]
            comp_bits = [ancilla[comp_start + i] for i in range(num_qubits_per_var)]
            final_flag = ancilla[flag_start + constraint_idx]
            multi_control_bits = [ancilla[multi_control_start + i] for i in range(multi_control_ancillas)]
            
            # XOR comparison with constant (reusing comparison ancillas)
            for i, bit in enumerate(reversed(const_bits)):
                const_qubit = const_one[0] if bit == '1' else const_zero[0]
                qc.cx(reg[i], comp_bits[i])
                operations.append(lambda r=reg[i], c=comp_bits[i]: qc.cx(r, c))
                qc.cx(const_qubit, comp_bits[i])
                operations.append(lambda cq=const_qubit, c=comp_bits[i]: qc.cx(cq, c))
            
            # Inequality logic (reusing multi-control ancillas)
            ops = self._add_inequality_logic(qc, comp_bits, final_flag, multi_control_bits, num_qubits_per_var)
            operations.extend(ops)
            
            constraint_idx += 1
        
        if reversible_with_phase:
            # Apply phase to all constraint flags
            # For simplicity, we'll mark the state where ALL constraints are satisfied
            if total_constraints == 1:
                qc.z(ancilla[flag_start])
            elif total_constraints == 2:
                qc.ccz(ancilla[flag_start], ancilla[flag_start + 1])
            else:
                # For more constraints, use multi-controlled Z
                self._add_multi_controlled_z(qc, [ancilla[flag_start + i] for i in range(total_constraints)], 
                                            [ancilla[multi_control_start + i] for i in range(multi_control_ancillas)])
            
            # Undo the operations in reverse order
            for op in reversed(operations):
                op()
        
        return qc
    
    def _add_inequality_logic(self, qc, comp_bits, final_flag, multi_control_bits, n):
        """Add logic to set final_flag = 1 if any comp_bit is 1 (inequality detected)"""
        ops = []
        if n == 1:
            qc.cx(comp_bits[0], final_flag)
            ops.append(lambda a=comp_bits[0], b=final_flag: qc.cx(a, b))
        elif n == 2:
            qc.ccx(comp_bits[0], comp_bits[1], final_flag)
            ops.append(lambda a=comp_bits[0], b=comp_bits[1], c=final_flag: qc.ccx(a, b, c))
        else:
            # Use multi-controlled OR: final_flag = comp_bits[0] OR comp_bits[1] OR ... OR comp_bits[n-1]
            # Implement as NOT(NOT(comp_bits[0]) AND NOT(comp_bits[1]) AND ... AND NOT(comp_bits[n-1]))
            
            # First flip all comparison bits
            for i in range(n):
                qc.x(comp_bits[i])
                ops.append(lambda q=comp_bits[i]: qc.x(q))
            
            # Multi-controlled X gate (all comp_bits must be 0 for gate to fire)
            if n == 3:
                # Use one multi_control_bit for 3-way gate
                qc.ccx(comp_bits[0], comp_bits[1], multi_control_bits[0])
                ops.append(lambda a=comp_bits[0], b=comp_bits[1], c=multi_control_bits[0]: qc.ccx(a, b, c))
                qc.ccx(multi_control_bits[0], comp_bits[2], final_flag)
                ops.append(lambda a=multi_control_bits[0], b=comp_bits[2], c=final_flag: qc.ccx(a, b, c))
                qc.ccx(comp_bits[0], comp_bits[1], multi_control_bits[0])  # Uncompute
                ops.append(lambda a=comp_bits[0], b=comp_bits[1], c=multi_control_bits[0]: qc.ccx(a, b, c))
            else:
                # For n > 3, build cascading multi-controlled gate
                temp = comp_bits[0]
                for i in range(1, n - 1):
                    if i == 1:
                        target = multi_control_bits[0] if len(multi_control_bits) > 0 else final_flag
                    else:
                        target = multi_control_bits[i-1] if i-1 < len(multi_control_bits) else final_flag
                    
                    if i < n - 1:
                        qc.ccx(temp, comp_bits[i], target)
                        ops.append(lambda a=temp, b=comp_bits[i], c=target: qc.ccx(a, b, c))
                        temp = target
                
                # Final gate to the actual flag
                qc.ccx(temp, comp_bits[n-1], final_flag)
                ops.append(lambda a=temp, b=comp_bits[n-1], c=final_flag: qc.ccx(a, b, c))
                
                # Uncompute in reverse order
                for i in range(n-2, 0, -1):
                    if i == 1:
                        source = multi_control_bits[0] if len(multi_control_bits) > 0 else final_flag
                    else:
                        source = multi_control_bits[i-1] if i-1 < len(multi_control_bits) else final_flag
                    
                    if i > 1:
                        prev_temp = comp_bits[0] if i == 2 else multi_control_bits[i-2]
                        qc.ccx(prev_temp, comp_bits[i], source)
                        ops.append(lambda a=prev_temp, b=comp_bits[i], c=source: qc.ccx(a, b, c))
            
            # Flip comparison bits back
            for i in range(n):
                qc.x(comp_bits[i])
                ops.append(lambda q=comp_bits[i]: qc.x(q))
        
        # Flip final result (we want 1 when inequality exists, not when equality exists)
        qc.x(final_flag)
        ops.append(lambda q=final_flag: qc.x(q))
        return ops
    
    def _add_multi_controlled_z(self, qc, control_qubits, ancilla_qubits):
        """Add a multi-controlled Z gate using available ancillas"""
        n = len(control_qubits)
        if n == 1:
            qc.z(control_qubits[0])
        elif n == 2:
            qc.cz(control_qubits[0], control_qubits[1])
        else:
            # Convert to multi-controlled X, apply Z, then undo
            # This is a simplified implementation - in practice you'd want a more efficient decomposition
            target = ancilla_qubits[0] if ancilla_qubits else None
            if target:
                # Multi-controlled X to ancilla
                if n == 3:
                    qc.ccx(control_qubits[0], control_qubits[1], ancilla_qubits[0])
                    qc.ccx(ancilla_qubits[0], control_qubits[2], target)
                    qc.z(target)
                    qc.ccx(ancilla_qubits[0], control_qubits[2], target)
                    qc.ccx(control_qubits[0], control_qubits[1], ancilla_qubits[0])


# Example usage with phase flip functionality
if __name__ == "__main__":
    # Example 4x4 Sudoku puzzle (0 represents empty cells)
    sample_puzzle = [
        [3, 1, 4, 2],
        [2, 0, 0, 1],
        [1, 0, 0, 0],
        [4, 0, 0, 3]
    ]
    
    qc = build_sudoku_circuit(sample_puzzle)
    print(qc)