import pytest
import stim

from main import make_noisy_heavy_hex_circuit


@pytest.mark.parametrize("diam,basis", [
    (d, b)
    for d in [3, 5, 7]
    for b in 'XZ'
])
def test_circuit_distance(diam: int, basis: str):
    circuit = make_noisy_heavy_hex_circuit(
        diam=diam,
        time_boundary_basis=basis,
        rounds=10,
        noise=1e-3,
    )

    # Verify errors decompose.
    circuit.detector_error_model(decompose_errors=True)

    # Verify expected distance.
    assert len(circuit.shortest_graphlike_error()) == diam


def test_exact_circuit():
    circuit = make_noisy_heavy_hex_circuit(
        diam=3,
        time_boundary_basis='X',
        rounds=100,
        noise=1e-3,
    )
    assert circuit == stim.Circuit("""
        QUBIT_COORDS(0, 0) 0
        QUBIT_COORDS(0, 0.5) 1
        QUBIT_COORDS(0, 1) 2
        QUBIT_COORDS(0, 1.5) 3
        QUBIT_COORDS(0, 2) 4
        QUBIT_COORDS(1, 0) 5
        QUBIT_COORDS(1, 0.5) 6
        QUBIT_COORDS(1, 1) 7
        QUBIT_COORDS(1, 1.5) 8
        QUBIT_COORDS(1, 2) 9
        QUBIT_COORDS(2, 0) 10
        QUBIT_COORDS(2, 0.5) 11
        QUBIT_COORDS(2, 1) 12
        QUBIT_COORDS(2, 1.5) 13
        QUBIT_COORDS(2, 2) 14
        QUBIT_COORDS(0.5, -0.5) 15
        QUBIT_COORDS(0.5, 1.5) 16
        QUBIT_COORDS(1.5, 0.5) 17
        QUBIT_COORDS(1.5, 2.5) 18
        R 0 2 4 5 7 9 10 12 14
        X_ERROR(0.001) 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 1 3 6 8 11 13 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        MPP(0.001) X5*X7*X10*X12 X9*X14
        DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
        TICK
        MPP(0.001) X0*X5 X2*X4*X7*X9
        DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
        TICK
        MPP(0.001) Z2*Z4 Z7*Z9 Z12*Z14
        DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
        TICK
        MPP(0.001) Z0*Z2 Z5*Z7 Z10*Z12
        DETECTOR(0.5, 0.5, 0) rec[-8] rec[-7]
        DETECTOR(1.5, 1.5, 0) rec[-10] rec[-9]
        DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
        TICK
        REPEAT 98 {
            MPP(0.001) X5*X7*X10*X12 X9*X14
            DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
            TICK
            MPP(0.001) X0*X5 X2*X4*X7*X9
            DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
            TICK
            MPP(0.001) Z2*Z4 Z7*Z9 Z12*Z14
            DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
            TICK
            MPP(0.001) Z0*Z2 Z5*Z7 Z10*Z12
            DETECTOR(0.5, 0.5, 0) rec[-18] rec[-17] rec[-8] rec[-7]
            DETECTOR(1.5, 1.5, 0) rec[-20] rec[-19] rec[-10] rec[-9]
            DETECTOR(0, 1.5, 0) rec[-16] rec[-6]
            DETECTOR(0.5, 0.5, 0) rec[-13] rec[-12] rec[-3] rec[-2]
            DETECTOR(1.5, 1.5, 0) rec[-15] rec[-14] rec[-5] rec[-4]
            DETECTOR(2, 0.5, 0) rec[-11] rec[-1]
            DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
            TICK
        }
        MPP(0.001) X5*X7*X10*X12 X9*X14
        DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
        TICK
        MPP(0.001) X0*X5 X2*X4*X7*X9
        DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
        TICK
        MPP(0.001) Z2*Z4 Z7*Z9 Z12*Z14
        DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
        TICK
        MPP(0.001) Z0*Z2 Z5*Z7 Z10*Z12
        DETECTOR(0.5, 0.5, 0) rec[-18] rec[-17] rec[-8] rec[-7]
        DETECTOR(1.5, 1.5, 0) rec[-20] rec[-19] rec[-10] rec[-9]
        DETECTOR(0, 1.5, 0) rec[-16] rec[-6]
        DETECTOR(0.5, 0.5, 0) rec[-13] rec[-12] rec[-3] rec[-2]
        DETECTOR(1.5, 1.5, 0) rec[-15] rec[-14] rec[-5] rec[-4]
        DETECTOR(2, 0.5, 0) rec[-11] rec[-1]
        DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        M(0.001) 0 2 4 5 7 9 10 12 14
        DETECTOR(0.5, 0.5, 0) rec[-17] rec[-16] rec[-9] rec[-8] rec[-7] rec[-6] rec[-5] rec[-4]
        DETECTOR(1.5, 1.5, 0) rec[-19] rec[-18] rec[-6] rec[-5] rec[-4] rec[-3] rec[-2] rec[-1]
        OBSERVABLE_INCLUDE(0) rec[-9] rec[-8] rec[-7]
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
    """)