import dataclasses
import functools
import pathlib
from typing import List, FrozenSet, Optional

import stim
from _builder import Builder, AtLayer
from _noise import NoiseModel, NoiseRule
from _viewer import stim_circuit_html_viewer


@dataclasses.dataclass
class Tile:
    data_qubits: List[Optional[complex]]
    measure_qubit: complex
    basis: str

    @functools.cached_property
    def data_set(self) -> FrozenSet[complex]:
        return frozenset(q
                         for q in self.data_qubits
                         if q is not None)

    @functools.cached_property
    def used_set(self) -> FrozenSet[complex]:
        return self.data_set | frozenset([self.measure_qubit])


def checkerboard_basis(c: complex) -> str:
    return 'Z' if (c.real + c.imag) % 2 == 1 else 'X'


def create_heavy_hex_tiles(diam: int) -> List[Tile]:
    all_data_set = {
        x + 1j*y
        for x in range(diam)
        for y in range(diam)
    }
    tiles = []
    top_basis = 'X'
    side_basis = 'Z'
    for x in range(-1, diam):
        for y in range(-1, diam):
            top_left = x + 1j*y
            center = top_left + 0.5 + 0.5j
            b = checkerboard_basis(center)
            on_top_or_bottom = y in [-1, diam - 1]
            on_side = x in [-1, diam - 1]
            if on_top_or_bottom and b != top_basis:
                continue
            if on_side and b != side_basis:
                continue

            data_qubits = [
                top_left,
                top_left + 1,
                top_left + 1j,
                top_left + 1 + 1j,
            ]
            if b == 'Z':
                continue
            for qi in range(4):
                if data_qubits[qi] not in all_data_set:
                    data_qubits[qi] = None
            if sum(e is not None for e in data_qubits) < 2:
                continue
            tiles.append(Tile(
                data_qubits=data_qubits,
                measure_qubit=center,
                basis=b,
            ))
    for x in range(diam):
        for y in range(diam - 1):
            q = x + y*1j
            tiles.append(Tile(
                data_qubits=[q, q + 1j],
                measure_qubit=q + 0.5j,
                basis='Z',
            ))
    return tiles


def make_heavy_hex_circuit(
        *,
        diam: int,
        time_boundary_basis: str,
        rounds: int,
) -> stim.Circuit:
    tiles = create_heavy_hex_tiles(diam)
    data_set = {q for tile in tiles for q in tile.data_set}
    used_set = {q for tile in tiles for q in tile.used_set}
    m2t = {tile.measure_qubit: tile for tile in tiles}

    x_combos = []
    for col in range(diam - 1):
        combined_tiles = []
        for row in range(-1, diam + 1):
            m = col + row * 1j + 0.5 + 0.5j
            if m in m2t:
                assert row != diam
                combined_tiles.append(m2t[m])
                assert m2t[m].basis == 'X'
        x_combos.append(combined_tiles)
    z_combos = []
    for x in range(-1, diam):
        for y in range(diam - 1):
            m = x + y * 1j + 0.5 + 0.5j
            if checkerboard_basis(m) == 'X':
                continue
            combined_tiles = []
            for m2 in [m - 0.5, m + 0.5]:
                if m2 in m2t:
                    combined_tiles.append(m2t[m2])
            if combined_tiles:
                z_combos.append(combined_tiles)

    builder = Builder.for_qubits(used_set)
    builder.gate("R", data_set)
    builder.tick()
    if time_boundary_basis == 'X':
        builder.gate("H", data_set)
        builder.tick()

    layer = 0
    for _ in range(rounds):
        for desired_parity in [False, True]:
            for tile in tiles:
                parity = tile.measure_qubit.real % 2 == 0.5
                if tile.basis == 'X' and parity == desired_parity:
                    builder.measure_pauli_product(
                        qs={tile.basis: tile.data_set},
                        key=tile.measure_qubit,
                        layer=layer,
                    )
            builder.tick()

        for desired_parity in [False, True]:
            for tile in tiles:
                parity = tile.measure_qubit.imag % 2 == 0.5
                if tile.basis == 'Z' and parity == desired_parity:
                    builder.measure_pauli_product(
                        qs={tile.basis: tile.data_set},
                        key=tile.measure_qubit,
                        layer=layer,
                    )
            builder.tick()

        # Combined X column detectors
        if layer > 0 or time_boundary_basis == 'X':
            for combined_tiles in x_combos:
                builder.detector([
                    AtLayer(tile.measure_qubit, layer - d)
                    for tile in combined_tiles
                    for d in ([0, 1] if layer > 0 else [0])
                ], pos=sum(tile.measure_qubit for tile in combined_tiles) / len(combined_tiles))

        # Z detectors
        if layer > 0 or time_boundary_basis == 'Z':
            for combined_tiles in z_combos:
                builder.detector([
                    AtLayer(tile.measure_qubit, layer - d)
                    for tile in combined_tiles
                    for d in ([0, 1] if layer > 0 else [0])
                ], pos=sum(tile.measure_qubit for tile in combined_tiles) / len(combined_tiles))
        layer += 1

    if time_boundary_basis == 'X':
        builder.gate('H', data_set)
        builder.tick()
    layer -= 1
    builder.measure(data_set, layer=layer)

    # Final X column detectors
    final_tiles = x_combos if time_boundary_basis == 'X' else z_combos
    for combined_tiles in final_tiles:
        builder.detector({
            AtLayer(q, layer)
            for tile in combined_tiles
            for q in tile.used_set
        }, pos=sum(tile.measure_qubit for tile in combined_tiles) / len(combined_tiles))

    if time_boundary_basis == 'X':
        obs_qubits = {q for q in data_set if q.real == 0}
    else:
        obs_qubits = {q for q in data_set if q.imag == 0}
    builder.obs_include([AtLayer(q, layer) for q in obs_qubits],
                        obs_index=0)
    return builder.circuit


def make_noise_model(noise: float) -> NoiseModel:
    return NoiseModel(
        idle_depolarization=noise,
        any_clifford_1q_rule=NoiseRule(after={'DEPOLARIZE1': noise}),
        any_clifford_2q_rule=NoiseRule(after={'DEPOLARIZE2': noise}),
        gate_rules={
            'R': NoiseRule(after={'X_ERROR': noise}),
        },
        measure_rules={
            'Z': NoiseRule(
                after={'DEPOLARIZE1': noise},
                flip_result=noise,
            ),
            'ZZ': NoiseRule(
                after={'DEPOLARIZE1': noise},
                flip_result=noise,
            ),
            'XX': NoiseRule(
                after={'DEPOLARIZE1': noise},
                flip_result=noise,
            ),
            'XXXX': NoiseRule(
                after={'DEPOLARIZE1': noise},
                flip_result=noise,
            ),
        }
    )

def main():
    circuits_dir = pathlib.Path('out/circuits')
    circuits_dir.mkdir(exist_ok=True, parents=True)

    for basis in 'XZ':
        for diam in [3, 5, 7]:
            for noise in [1e-4, 5e-4, 1e-3, 5e-3, 1e-2]:
                ideal_circuit = make_heavy_hex_circuit(
                    diam=diam,
                    time_boundary_basis=basis,
                    rounds=diam * 3,
                )
                noisy_circuit = make_noise_model(noise).noisy_circuit(ideal_circuit)

                # Verify workable
                noisy_circuit.detector_error_model(decompose_errors=True)

                path = circuits_dir / f'd={diam},p={noise},b={basis}.stim'
                with open(path, 'w') as f:
                    print(noisy_circuit, file=f)
                print("wrote", path)

    with open('out/viewer.html', 'w') as f:
        print(stim_circuit_html_viewer(ideal_circuit), file=f)



if __name__ == '__main__':
    main()
