import pytest
import stim

from main import make_noisy_heavy_hex_circuit


@pytest.mark.parametrize("diam,basis,gate_set", [
    (d, b, g)
    for d in [3, 5, 7]
    for b in 'XZ'
    for g in ['mpp', 'cx']
])
def test_circuit_distance(diam: int, basis: str, gate_set: str):
    circuit = make_noisy_heavy_hex_circuit(
        diam=diam,
        time_boundary_basis=basis,
        rounds=10,
        noise=1e-3,
        gate_set=gate_set,
    )

    # Verify errors decompose.
    circuit.detector_error_model(decompose_errors=True)

    # Verify expected graphlike distance.
    assert len(circuit.shortest_graphlike_error()) == diam

    # More expensive distance verification, beyond graphlike errors.
    assert len(circuit.search_for_undetectable_logical_errors(
        dont_explore_detection_event_sets_with_size_above=6,
        dont_explore_edges_increasing_symptom_degree=False,
        dont_explore_edges_with_degree_above=999,
        canonicalize_circuit_errors=True,
    )) == diam


def test_exact_circuit_mpp():
    circuit = make_noisy_heavy_hex_circuit(
        diam=3,
        time_boundary_basis='X',
        rounds=100,
        noise=1e-3,
        gate_set='mpp',
    )
    assert stim.Circuit(str(circuit)) == stim.Circuit("""
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
        QUBIT_COORDS(0.5, 0) 15
        QUBIT_COORDS(0.5, 1.5) 16
        QUBIT_COORDS(1.5, 0.5) 17
        QUBIT_COORDS(1.5, 2) 18
        R 0 2 4 5 7 9 10 12 14
        X_ERROR(0.000666667) 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 1 3 6 8 11 13 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        MPP(0.000666667) X5*X7*X10*X12 X9*X14
        DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
        TICK
        MPP(0.000666667) X0*X5 X2*X4*X7*X9
        DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
        TICK
        MPP(0.000666667) Z2*Z4 Z7*Z9 Z12*Z14
        DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
        TICK
        MPP(0.000666667) Z0*Z2 Z5*Z7 Z10*Z12
        DETECTOR(0.5, -10, 0) rec[-8] rec[-7]
        DETECTOR(1.5, -10, 0) rec[-10] rec[-9]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
        TICK
        REPEAT 98 {
            MPP(0.000666667) X5*X7*X10*X12 X9*X14
            DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
            TICK
            MPP(0.000666667) X0*X5 X2*X4*X7*X9
            DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
            TICK
            MPP(0.000666667) Z2*Z4 Z7*Z9 Z12*Z14
            DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
            TICK
            MPP(0.000666667) Z0*Z2 Z5*Z7 Z10*Z12
            DETECTOR(0.5, -10, 0) rec[-18] rec[-17] rec[-8] rec[-7]
            DETECTOR(1.5, -10, 0) rec[-20] rec[-19] rec[-10] rec[-9]
            DETECTOR(0, 1.5, 0) rec[-16] rec[-6]
            DETECTOR(0.5, 0.5, 0) rec[-13] rec[-12] rec[-3] rec[-2]
            DETECTOR(1.5, 1.5, 0) rec[-15] rec[-14] rec[-5] rec[-4]
            DETECTOR(2, 0.5, 0) rec[-11] rec[-1]
            SHIFT_COORDS(0, 0, 1)
            DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
            TICK
        }
        MPP(0.000666667) X5*X7*X10*X12 X9*X14
        DEPOLARIZE1(0.001) 5 7 10 12 9 14 0 1 2 3 4 6 8 11 13 15 16 17 18
        TICK
        MPP(0.000666667) X0*X5 X2*X4*X7*X9
        DEPOLARIZE1(0.001) 0 5 2 4 7 9 1 3 6 8 10 11 12 13 14 15 16 17 18
        TICK
        MPP(0.000666667) Z2*Z4 Z7*Z9 Z12*Z14
        DEPOLARIZE1(0.001) 2 4 7 9 12 14 0 1 3 5 6 8 10 11 13 15 16 17 18
        TICK
        MPP(0.000666667) Z0*Z2 Z5*Z7 Z10*Z12
        DETECTOR(0.5, -10, 0) rec[-18] rec[-17] rec[-8] rec[-7]
        DETECTOR(1.5, -10, 0) rec[-20] rec[-19] rec[-10] rec[-9]
        DETECTOR(0, 1.5, 0) rec[-16] rec[-6]
        DETECTOR(0.5, 0.5, 0) rec[-13] rec[-12] rec[-3] rec[-2]
        DETECTOR(1.5, 1.5, 0) rec[-15] rec[-14] rec[-5] rec[-4]
        DETECTOR(2, 0.5, 0) rec[-11] rec[-1]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 0 2 5 7 10 12 1 3 4 6 8 9 11 13 14 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        M(0.000666667) 0 2 4 5 7 9 10 12 14
        DETECTOR(0.5, -10, 0) rec[-17] rec[-16] rec[-9] rec[-8] rec[-7] rec[-6] rec[-5] rec[-4]
        DETECTOR(1.5, -10, 0) rec[-19] rec[-18] rec[-6] rec[-5] rec[-4] rec[-3] rec[-2] rec[-1]
        OBSERVABLE_INCLUDE(0) rec[-9] rec[-8] rec[-7]
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
    """)


def test_exact_circuit_cx():
    circuit = make_noisy_heavy_hex_circuit(
        diam=3,
        time_boundary_basis='X',
        rounds=100,
        noise=1e-3,
        gate_set='cx',
    )
    assert stim.Circuit(str(circuit)) == stim.Circuit("""
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
        QUBIT_COORDS(0.5, 0) 15
        QUBIT_COORDS(0.5, 1.5) 16
        QUBIT_COORDS(1.5, 0.5) 17
        QUBIT_COORDS(1.5, 2) 18
        R 0 2 4 5 7 9 10 12 14
        X_ERROR(0.000666667) 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 1 3 6 8 11 13 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        R 1 3 6 8 11 13 15 16 17 18
        X_ERROR(0.000666667) 1 3 6 8 11 13 15 16 17 18
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14
        TICK
        H 15 16 17 18
        DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
        TICK
        CX 16 8 17 11
        DEPOLARIZE2(0.001) 16 8 17 11
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 9 10 12 13 14 15 18
        TICK
        CX 8 7 11 10 16 3 17 6
        DEPOLARIZE2(0.001) 8 7 11 10 16 3 17 6
        DEPOLARIZE1(0.001) 0 1 2 4 5 9 12 13 14 15 18
        TICK
        CX 8 9 11 12 3 4 6 7 15 5
        DEPOLARIZE2(0.001) 8 9 11 12 3 4 6 7 15 5
        DEPOLARIZE1(0.001) 0 1 2 10 13 14 16 17 18
        TICK
        CX 3 2 6 5 16 8 17 11 15 0 18 14
        DEPOLARIZE2(0.001) 3 2 6 5 16 8 17 11 15 0 18 14
        DEPOLARIZE1(0.001) 1 4 7 9 10 12 13
        TICK
        CX 16 3 17 6 18 9
        DEPOLARIZE2(0.001) 16 3 17 6 18 9
        DEPOLARIZE1(0.001) 0 1 2 4 5 7 8 10 11 12 13 14 15
        TICK
        H 15 16 17 18
        DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
        TICK
        M(0.000666667) 15 16 17 18 3 6 8 11
        DETECTOR(1.25, 1.75, 0) rec[-2]
        DETECTOR(0.25, 1.75, 0) rec[-4]
        DETECTOR(2.25, 0.75, 0) rec[-1]
        DETECTOR(1.25, 0.75, 0) rec[-3]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 15 16 17 18 3 6 8 11 0 1 2 4 5 7 9 10 12 13 14
        TICK
        R 1 3 6 8 11 13
        X_ERROR(0.000666667) 1 3 6 8 11 13
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 15 16 17 18
        TICK
        CX 0 1 7 8 10 11
        DEPOLARIZE2(0.001) 0 1 7 8 10 11
        DEPOLARIZE1(0.001) 2 3 4 5 6 9 12 13 14 15 16 17 18
        TICK
        CX 2 1 9 8 12 11 4 3 7 6 14 13
        DEPOLARIZE2(0.001) 2 1 9 8 12 11 4 3 7 6 14 13
        DEPOLARIZE1(0.001) 0 5 10 15 16 17 18
        TICK
        CX 2 3 5 6 12 13
        DEPOLARIZE2(0.001) 2 3 5 6 12 13
        DEPOLARIZE1(0.001) 0 1 4 7 8 9 10 11 14 15 16 17 18
        TICK
        M(0.000666667) 1 3 6 8 11 13
        DETECTOR(0.5, -10, 0) rec[-14] rec[-13]
        DETECTOR(1.5, -10, 0) rec[-12] rec[-11]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 1 3 6 8 11 13 0 2 4 5 7 9 10 12 14 15 16 17 18
        TICK
        REPEAT 98 {
            R 1 3 6 8 11 13 15 16 17 18
            X_ERROR(0.000666667) 1 3 6 8 11 13 15 16 17 18
            DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14
            TICK
            H 15 16 17 18
            DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
            TICK
            CX 16 8 17 11
            DEPOLARIZE2(0.001) 16 8 17 11
            DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 9 10 12 13 14 15 18
            TICK
            CX 8 7 11 10 16 3 17 6
            DEPOLARIZE2(0.001) 8 7 11 10 16 3 17 6
            DEPOLARIZE1(0.001) 0 1 2 4 5 9 12 13 14 15 18
            TICK
            CX 8 9 11 12 3 4 6 7 15 5
            DEPOLARIZE2(0.001) 8 9 11 12 3 4 6 7 15 5
            DEPOLARIZE1(0.001) 0 1 2 10 13 14 16 17 18
            TICK
            CX 3 2 6 5 16 8 17 11 15 0 18 14
            DEPOLARIZE2(0.001) 3 2 6 5 16 8 17 11 15 0 18 14
            DEPOLARIZE1(0.001) 1 4 7 9 10 12 13
            TICK
            CX 16 3 17 6 18 9
            DEPOLARIZE2(0.001) 16 3 17 6 18 9
            DEPOLARIZE1(0.001) 0 1 2 4 5 7 8 10 11 12 13 14 15
            TICK
            H 15 16 17 18
            DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
            TICK
            M(0.000666667) 15 16 17 18 3 6 8 11
            DETECTOR(1.25, 1.75, 0) rec[-2]
            DETECTOR(0.25, 1.75, 0) rec[-4]
            DETECTOR(2.25, 0.75, 0) rec[-1]
            DETECTOR(1.25, 0.75, 0) rec[-3]
            SHIFT_COORDS(0, 0, 1)
            DEPOLARIZE1(0.001) 15 16 17 18 3 6 8 11 0 1 2 4 5 7 9 10 12 13 14
            TICK
            R 1 3 6 8 11 13
            X_ERROR(0.000666667) 1 3 6 8 11 13
            DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 15 16 17 18
            TICK
            CX 0 1 7 8 10 11
            DEPOLARIZE2(0.001) 0 1 7 8 10 11
            DEPOLARIZE1(0.001) 2 3 4 5 6 9 12 13 14 15 16 17 18
            TICK
            CX 2 1 9 8 12 11 4 3 7 6 14 13
            DEPOLARIZE2(0.001) 2 1 9 8 12 11 4 3 7 6 14 13
            DEPOLARIZE1(0.001) 0 5 10 15 16 17 18
            TICK
            CX 2 3 5 6 12 13
            DEPOLARIZE2(0.001) 2 3 5 6 12 13
            DEPOLARIZE1(0.001) 0 1 4 7 8 9 10 11 14 15 16 17 18
            TICK
            M(0.000666667) 1 3 6 8 11 13
            DETECTOR(0.5, -10, 0) rec[-28] rec[-27] rec[-14] rec[-13]
            DETECTOR(1.5, -10, 0) rec[-26] rec[-25] rec[-12] rec[-11]
            DETECTOR(0, 1.5, 0) rec[-19] rec[-5]
            DETECTOR(0.5, 0.5, 0) rec[-20] rec[-18] rec[-6] rec[-4]
            DETECTOR(1.5, 1.5, 0) rec[-17] rec[-15] rec[-3] rec[-1]
            DETECTOR(2, 0.5, 0) rec[-16] rec[-2]
            SHIFT_COORDS(0, 0, 1)
            DEPOLARIZE1(0.001) 1 3 6 8 11 13 0 2 4 5 7 9 10 12 14 15 16 17 18
            TICK
        }
        R 1 3 6 8 11 13 15 16 17 18
        X_ERROR(0.000666667) 1 3 6 8 11 13 15 16 17 18
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14
        TICK
        H 15 16 17 18
        DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
        TICK
        CX 16 8 17 11
        DEPOLARIZE2(0.001) 16 8 17 11
        DEPOLARIZE1(0.001) 0 1 2 3 4 5 6 7 9 10 12 13 14 15 18
        TICK
        CX 8 7 11 10 16 3 17 6
        DEPOLARIZE2(0.001) 8 7 11 10 16 3 17 6
        DEPOLARIZE1(0.001) 0 1 2 4 5 9 12 13 14 15 18
        TICK
        CX 8 9 11 12 3 4 6 7 15 5
        DEPOLARIZE2(0.001) 8 9 11 12 3 4 6 7 15 5
        DEPOLARIZE1(0.001) 0 1 2 10 13 14 16 17 18
        TICK
        CX 3 2 6 5 16 8 17 11 15 0 18 14
        DEPOLARIZE2(0.001) 3 2 6 5 16 8 17 11 15 0 18 14
        DEPOLARIZE1(0.001) 1 4 7 9 10 12 13
        TICK
        CX 16 3 17 6 18 9
        DEPOLARIZE2(0.001) 16 3 17 6 18 9
        DEPOLARIZE1(0.001) 0 1 2 4 5 7 8 10 11 12 13 14 15
        TICK
        H 15 16 17 18
        DEPOLARIZE1(0.001) 15 16 17 18 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14
        TICK
        M(0.000666667) 15 16 17 18 3 6 8 11
        DETECTOR(1.25, 1.75, 0) rec[-2]
        DETECTOR(0.25, 1.75, 0) rec[-4]
        DETECTOR(2.25, 0.75, 0) rec[-1]
        DETECTOR(1.25, 0.75, 0) rec[-3]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 15 16 17 18 3 6 8 11 0 1 2 4 5 7 9 10 12 13 14
        TICK
        R 1 3 6 8 11 13
        X_ERROR(0.000666667) 1 3 6 8 11 13
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 15 16 17 18
        TICK
        CX 0 1 7 8 10 11
        DEPOLARIZE2(0.001) 0 1 7 8 10 11
        DEPOLARIZE1(0.001) 2 3 4 5 6 9 12 13 14 15 16 17 18
        TICK
        CX 2 1 9 8 12 11 4 3 7 6 14 13
        DEPOLARIZE2(0.001) 2 1 9 8 12 11 4 3 7 6 14 13
        DEPOLARIZE1(0.001) 0 5 10 15 16 17 18
        TICK
        CX 2 3 5 6 12 13
        DEPOLARIZE2(0.001) 2 3 5 6 12 13
        DEPOLARIZE1(0.001) 0 1 4 7 8 9 10 11 14 15 16 17 18
        TICK
        M(0.000666667) 1 3 6 8 11 13
        DETECTOR(0.5, -10, 0) rec[-28] rec[-27] rec[-14] rec[-13]
        DETECTOR(1.5, -10, 0) rec[-26] rec[-25] rec[-12] rec[-11]
        DETECTOR(0, 1.5, 0) rec[-19] rec[-5]
        DETECTOR(0.5, 0.5, 0) rec[-20] rec[-18] rec[-6] rec[-4]
        DETECTOR(1.5, 1.5, 0) rec[-17] rec[-15] rec[-3] rec[-1]
        DETECTOR(2, 0.5, 0) rec[-16] rec[-2]
        SHIFT_COORDS(0, 0, 1)
        DEPOLARIZE1(0.001) 1 3 6 8 11 13 0 2 4 5 7 9 10 12 14 15 16 17 18
        TICK
        H 0 2 4 5 7 9 10 12 14
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
        TICK
        M(0.000666667) 0 2 4 5 7 9 10 12 14
        DETECTOR(0.5, -10, 0) rec[-23] rec[-22] rec[-9] rec[-8] rec[-7] rec[-6] rec[-5] rec[-4]
        DETECTOR(1.5, -10, 0) rec[-21] rec[-20] rec[-6] rec[-5] rec[-4] rec[-3] rec[-2] rec[-1]
        OBSERVABLE_INCLUDE(0) rec[-9] rec[-8] rec[-7]
        DEPOLARIZE1(0.001) 0 2 4 5 7 9 10 12 14 1 3 6 8 11 13 15 16 17 18
    """)
