from typing import List
from qiskit.circuit import QuantumCircuit, QuantumRegister, AncillaRegister, Parameter
from qiskit.quantum_info import Statevector
import numpy as np
import PuzzleConfigurations as pc

def solve_sudoqu(puzzle : List[List[int]]):
    # We  find all configurations for rows/columns/quadrants and complete the values which can be trivially filled.
    pc.complete_all_trivial_missing_values(puzzle)

    # Count remaining unknowns
    number_of_unknowns = 0
    for row in puzzle:
        number_of_unknowns += row.count(0)

    # Then we convert the board into row/column/square constraints.
    constraints = pc.row_possible_values(puzzle) + pc.column_possible_values(puzzle) + pc.square_possible_values(puzzle)
    constraints = [constraint for constraint in constraints if constraint[0] != [] ]
    number_of_constraints = len(constraints)

    # Our next step is to initiate our qubits and a circuit. Let n be the number of unknowns on the board after completing obvous unknowns.
    # To represent the four numbers 1, 2, 3, 4 we will need 2 bits. Each bit we can then represent via a quibit in the obvious way:
    # 0 \mapsto |0> and 1 \mapsto |1>. Thus we need two qubits to represent the four numbers 1, 2, 3, 4 via qubits.
    # Hence, we initiate 2n qubits for the unknowns. 
    # Notation: We will use the number 0 to represent an unknown on the board.
    # To save space, we will then represent the numbers 1, 2, 3, 4 as follows via bits: 1\mapsto 00,
    # 2 \mapsto 01
    # 3 \mapsto 10 
    # 4 \mapsto 11.
    # Notation: Let i be an integer from 0 to n-1. We denote by u_i the qubit corresponding to the zeroth bit
    # of the i-th unknown and by t_i the first bit of the i-th unknown. For example, if the 7-th unknown ends up being 3,
    # we represent it with the bits 10 and thus u_7=0 and t_7=1.
    quantum_register_u = QuantumRegister(size=number_of_unknowns, name="u") #first bit of each unknown
    quantum_register_t = QuantumRegister(size=number_of_unknowns, name="t") #second bit of each unknown
    ancilla_register = AncillaRegister(size=number_of_constraints + 1, name="a") #ancilla bits for the sudoku constraints

    quantum_circuit = QuantumCircuit(quantum_register_u, quantum_register_t, ancilla_register, name="sudoqu")

    # We define more helpful variables.
    # Create a dictionary to map numbers to bit values as described above. We use the [u, t] ordering.
    number_to_bit = {
        1: [0, 0],
        2: [1, 0],
        3: [0, 1],
        4: [1, 1]
    }

    # Create a dictionary to map cell positions to 2-qubit indices
    c_to_q = {}
    for row in range(len(puzzle)):
        for col in range(len(puzzle[row])): 
            if puzzle[row][col] == 0:
                c_to_q[(row, col)] = len(c_to_q)

    # Create a two-bit equality checker xor-gate: first two qubits are the two-bit number to be checked, the last is the zero ancilla.
    # The bits come out to be 1 if they match.
    number_checker = {}
    for i in number_to_bit:
        number_checker[i] = QuantumCircuit(3)
        for j in range(2):
            if number_to_bit[i][j] == 1:
                number_checker[i].x(j)
            number_checker[i].cx(2, j)
            number_checker[i].x(j)
        number_checker[i] = number_checker[i].to_gate()

    # We will now need to add gates to check if the given qubits satisfy valid configurations for each row/column/quadrant.
    # We store such validness result on he ancilla qubits, starting from index 1. We transform any qubits coinciding with a 
    # valid configuration into 1, then flip the corresponding ancilla if all bits are correct, using a multi-controlled X gate.
    # We need to take care to then uncompute such transformations on non-ancillas.
    # Start checking constraints
    for const_idx in range(len(constraints)):
        constraint = constraints[const_idx]
        indices = [c_to_q[coord] for coord in constraint[0]]
        for permutation in constraint[1]:
            for i in range(len(indices)):
                qubit_idx = indices[i]
                quantum_circuit.compose(number_checker[permutation[i]], qubits = [quantum_register_u[qubit_idx], quantum_register_t[qubit_idx], ancilla_register[0]], inplace = True)
            quantum_circuit.mcx([quantum_register_u[qubit_idx] for qubit_idx in indices]+[quantum_register_t[qubit_idx] for qubit_idx in indices], ancilla_register[const_idx + 1])
            for i in range(len(indices)):
                qubit_idx = indices[i]
                quantum_circuit.compose(number_checker[permutation[i]].inverse(), qubits = [quantum_register_u[qubit_idx], quantum_register_t[qubit_idx], ancilla_register[0]], inplace = True)

    # Let us store the half-marker thus constructed (i.e. before multi-controlled Z puts a minus sign on the sought after configuration)
    # as a gate.
    half_marker = quantum_circuit.to_gate()

    # We now complete the rest of the marker circuit and save it as a gate.
    quantum_circuit.mcp(np.pi, ancilla_register[1:-1], ancilla_register[-1])
    quantum_circuit.compose(half_marker.inverse(),qubits = quantum_register_u[:] + quantum_register_t[:] + ancilla_register[:], inplace=True)

    marker_circuit = quantum_circuit.to_gate()

    n = 2*number_of_unknowns
    N = 2**n
    K = int(np.rint(np.pi / (4 * np.arcsin(1 / np.sqrt(N))) - 1/2))

    grover_circuit = QuantumCircuit(quantum_register_u,quantum_register_t, ancilla_register, name="Grover circuit")

    grover_circuit.h(range(n))
    for idx in range(K):
        grover_circuit.compose(marker_circuit, qubits = quantum_register_u[:] + quantum_register_t[:] + ancilla_register[:], inplace = True)
        grover_circuit.h(range(n))
        grover_circuit.x(range(n))
        grover_circuit.mcp(np.pi, quantum_register_u[:] + quantum_register_t[:-1], quantum_register_t[-1])
        grover_circuit.x(range(n))
        grover_circuit.h(range(n))

    psi = Statevector(grover_circuit)
    prob_dict = psi.probabilities_dict()
    max_key = max(prob_dict, key=prob_dict.get)
    for row, col in c_to_q:
        idx = c_to_q[(row, col)]
        puzzle[row][col] = 1+int(max_key[-1-idx])+2*int(max_key[-number_of_unknowns -1-idx])

    return puzzle

def main():
    puzzle: List[List[int]] = [
        [0, 0, 2, 3],
        [0, 2, 0, 4],
        [0, 1, 3, 0],
        [0, 0, 4, 1]
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

if __name__ == "__main__":
    main()