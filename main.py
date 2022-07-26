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
    def m(self) -> complex:
        return self.measure_qubit

    @functools.cached_property
    def degree(self) -> int:
        return len(self.data_set)

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
            degree = sum(e is not None for e in data_qubits)
            if degree < 2:
                continue
            rem_center = sum(q for q in data_qubits if q is not None) / degree
            tiles.append(Tile(
                data_qubits=data_qubits,
                measure_qubit=rem_center,
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


def make_mpp_based_round(*,
                         layer: int,
                         tiles: List[Tile],
                         builder: Builder,
                         time_boundary_basis: str,
                         x_combos: List[List[Tile]],
                         z_combos: List[List[Optional[Tile]]]):
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
        if not desired_parity:
            builder.tick()

    # Combined X column detectors
    if layer > 0 or time_boundary_basis == 'X':
        for combined_tiles in x_combos:
            pos = sum(tile.measure_qubit for tile in combined_tiles) / len(combined_tiles)
            pos = pos.real - 10j
            builder.detector([
                AtLayer(tile.measure_qubit, layer - d)
                for tile in combined_tiles
                for d in ([0, 1] if layer > 0 else [0])
            ], pos=pos)

    # Z detectors
    if layer > 0 or time_boundary_basis == 'Z':
        for combined_tiles in z_combos:
            kept_tiles = [tile for tile in combined_tiles if tile is not None]
            builder.detector([
                AtLayer(tile.measure_qubit, layer - d)
                for tile in kept_tiles
                for d in ([0, 1] if layer > 0 else [0])
            ], pos=sum(tile.measure_qubit for tile in kept_tiles) / len(kept_tiles))
    builder.shift_coords(dt=1)
    builder.tick()


def make_cx_based_round(*,
                        layer: int,
                        tiles: List[Tile],
                        builder: Builder,
                        time_boundary_basis: str,
                        x_combos: List[List[Tile]],
                        z_combos: List[List[Optional[Tile]]]):
    # step = 1
    builder.gate("R", [t.m for t in tiles])
    builder.tick()
    builder.gate("H", [t.m for t in tiles if t.basis == 'X'])
    builder.tick()
    # step = 2
    builder.cx([
        (t.m, t.m + 0.5)
        for t in tiles
        if t.degree == 4
    ])
    builder.tick()
    # step = 3
    builder.cx([
        (t.m + 0.5, t.m + 0.5 - 0.5j)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m, t.m - 0.5)
        for t in tiles
        if t.degree == 4
    ])
    builder.tick()
    # step = 4
    builder.cx([
        (t.m + 0.5, t.m + 0.5 + 0.5j)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m - 0.5, t.m - 0.5 + 0.5j)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m, t.m + 0.5)
        for t in tiles
        if t.basis == 'X'
        if t.degree == 2
        if t.data_qubits[0] is None  # (on top of patch)
    ])
    builder.tick()
    # step = 5
    builder.cx([
        (t.m - 0.5, t.m - 0.5 - 0.5j)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m, t.m + 0.5)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m, t.m - 0.5)
        for t in tiles
        if t.basis == 'X'
        if t.degree == 2
        if t.data_qubits[0] is None  # (on top of patch)
    ])
    builder.cx([
        (t.m, t.m + 0.5)
        for t in tiles
        if t.basis == 'X'
        if t.degree == 2
        if t.data_qubits[0] is not None  # (on bottom of patch)
    ])
    builder.tick()
    # step = 6
    builder.cx([
        (t.m, t.m - 0.5)
        for t in tiles
        if t.degree == 4
    ])
    builder.cx([
        (t.m, t.m - 0.5)
        for t in tiles
        if t.basis == 'X'
        if t.degree == 2
        if t.data_qubits[0] is not None  # (on bottom of patch)
    ])
    builder.tick()
    # step = 7
    builder.gate("H", [t.m for t in tiles if t.basis == 'X'])
    builder.tick()
    builder.measure([t.m for t in tiles if t.basis == 'X'], layer=layer)
    flags = [
        t.m + d
        for t in tiles
        if t.basis == 'X' and t.degree == 4
        for d in [0.5, -0.5]
    ]
    builder.measure(flags,
                    layer=layer,
                    tracker_key=lambda c: ('flag', c))
    for f in flags:
        builder.detector([AtLayer(('flag', f), layer)], pos=f + 0.25 + 0.25j)
    builder.shift_coords(dt=1)
    builder.tick()
    builder.gate('R', [t.m for t in tiles if t.basis == 'Z'])
    builder.tick()
    # step = 8
    builder.cx([
        (left.m - 0.5j, left.m)
        for left, right in z_combos
        if left is not None
    ])
    builder.tick()
    # step = 9
    builder.cx([
        (left.m + 0.5j, left.m)
        for left, right in z_combos
        if left is not None
    ])
    builder.cx([
        (right.m + 0.5j, right.m)
        for left, right in z_combos
        if right is not None
    ])
    builder.tick()
    # step = 10
    builder.cx([
        (right.m - 0.5j, right.m)
        for left, right in z_combos
        if right is not None
    ])
    builder.tick()
    # step = 11
    builder.measure([t.m for t in tiles if t.basis == 'Z'], layer=layer)

    # Combined X column detectors
    if layer > 0 or time_boundary_basis == 'X':
        for combined_tiles in x_combos:
            pos = sum(tile.measure_qubit for tile in combined_tiles) / len(combined_tiles)
            pos = pos.real - 10j
            builder.detector([
                AtLayer(tile.measure_qubit, layer - d)
                for tile in combined_tiles
                for d in ([0, 1] if layer > 0 else [0])
            ], pos=pos)

    # Z detectors
    if layer > 0 or time_boundary_basis == 'Z':
        for combined_tiles in z_combos:
            kept_tiles = [tile for tile in combined_tiles if tile is not None]
            pos = sum(tile.measure_qubit for tile in kept_tiles) / len(kept_tiles)
            builder.detector([
                AtLayer(tile.measure_qubit, layer - d)
                for tile in kept_tiles
                for d in ([0, 1] if layer > 0 else [0])
            ], pos=pos)
    builder.shift_coords(dt=1)
    builder.tick()


def make_heavy_hex_circuit(
        *,
        diam: int,
        time_boundary_basis: str,
        rounds: int,
        gate_set: str,
) -> stim.Circuit:
    tiles = create_heavy_hex_tiles(diam)
    data_set = {q for tile in tiles for q in tile.data_set}
    used_set = {q for tile in tiles for q in tile.used_set}
    m2t = {tile.measure_qubit: tile for tile in tiles}
    for tile in tiles:
        if tile.basis == 'X' and tile.degree == 2:
            if tile.data_qubits[0] is None:  # top of patch
                m2t[tile.m - 0.5j] = tile
            else:
                m2t[tile.m + 0.5j] = tile

    x_combos: List[List[Tile]] = []
    for col in range(diam - 1):
        combined_tiles = []
        for row in range(-1, diam + 1):
            m = col + row * 1j + 0.5 + 0.5j
            if m in m2t:
                assert row != diam
                combined_tiles.append(m2t[m])
                assert m2t[m].basis == 'X'
        x_combos.append(combined_tiles)
    z_combos: List[List[Optional[Tile]]] = []
    for x in range(-1, diam):
        for y in range(diam - 1):
            m = x + y * 1j + 0.5 + 0.5j
            if checkerboard_basis(m) == 'X':
                continue
            combined_tiles = []
            for m2 in [m - 0.5, m + 0.5]:
                if m2 in m2t:
                    combined_tiles.append(m2t[m2])
                else:
                    combined_tiles.append(None)
            if combined_tiles:
                z_combos.append(combined_tiles)

    builder = Builder.for_qubits(used_set)
    builder.gate("R", data_set)
    builder.tick()
    if time_boundary_basis == 'X':
        builder.gate("H", data_set)
        builder.tick()

    if gate_set == 'mpp':
        round_maker = make_mpp_based_round
    elif gate_set == 'cx':
        round_maker = make_cx_based_round
    else:
        raise NotImplementedError(f'{gate_set=}')

    assert rounds >= 2
    round_maker(layer=0,
                tiles=tiles,
                builder=builder,
                time_boundary_basis=time_boundary_basis,
                x_combos=x_combos,
                z_combos=z_combos)

    head = builder.circuit.copy()
    builder.circuit.clear()
    layer = 1
    round_maker(layer=1,
                tiles=tiles,
                builder=builder,
                time_boundary_basis=time_boundary_basis,
                x_combos=x_combos,
                z_combos=z_combos)

    if rounds > 2:
        builder.circuit *= (rounds - 2)
        layer += 1
        round_maker(layer=layer,
                    tiles=tiles,
                    builder=builder,
                    time_boundary_basis=time_boundary_basis,
                    x_combos=x_combos,
                    z_combos=z_combos)

    if time_boundary_basis == 'X':
        builder.gate('H', data_set)
        builder.tick()
    builder.measure(data_set, layer=layer)

    # Final detectors
    final_tiles = x_combos if time_boundary_basis == 'X' else z_combos
    for combined_tiles in final_tiles:
        kept_tiles = [tile for tile in combined_tiles if tile is not None]
        pos = sum(tile.measure_qubit for tile in kept_tiles) / len(kept_tiles)
        if time_boundary_basis == 'X':
            pos = pos.real - 10j
        builder.detector({
            AtLayer(q, layer)
            for tile in kept_tiles
            for q in tile.used_set
        }, pos=pos)

    if time_boundary_basis == 'X':
        obs_qubits = {q for q in data_set if q.real == 0}
    else:
        obs_qubits = {q for q in data_set if q.imag == 0}
    builder.obs_include([AtLayer(q, layer) for q in obs_qubits],
                        obs_index=0)
    return head + builder.circuit


def make_noise_model(noise: float, allow_mpp: bool) -> NoiseModel:
    result_flip_p = 2/3*noise
    mpp_rules = {
        'ZZ': NoiseRule(
            after={'DEPOLARIZE1': noise},
            flip_result=result_flip_p,
        ),
        'XX': NoiseRule(
            after={'DEPOLARIZE1': noise},
            flip_result=result_flip_p,
        ),
        'XXXX': NoiseRule(
            after={'DEPOLARIZE1': noise},
            flip_result=result_flip_p,
        ),
    }
    if not allow_mpp:
        mpp_rules = {}
    return NoiseModel(
        idle_depolarization=noise,
        any_clifford_1q_rule=NoiseRule(after={'DEPOLARIZE1': noise}),
        gate_rules={
            'R': NoiseRule(after={'X_ERROR': result_flip_p}),
            'CX': NoiseRule(after={'DEPOLARIZE2': noise}),
        },
        measure_rules={
            'Z': NoiseRule(
                after={'DEPOLARIZE1': noise},
                flip_result=result_flip_p,
            ),
            **mpp_rules,
        }
    )

def make_noisy_heavy_hex_circuit(
        *,
        diam: int,
        time_boundary_basis: str,
        rounds: int,
        noise: float,
        gate_set: str,
) -> stim.Circuit:
    ideal_circuit = make_heavy_hex_circuit(
        diam=diam,
        time_boundary_basis=time_boundary_basis,
        rounds=rounds,
        gate_set=gate_set,
    )
    noise_model = make_noise_model(noise, allow_mpp=gate_set=='mpp')
    return noise_model.noisy_circuit(ideal_circuit)


def main():
    circuits_dir = pathlib.Path('out/circuits')
    circuits_dir.mkdir(exist_ok=True, parents=True)

    for basis in 'XZ':
        for diam in [3, 5, 7, 9, 11, 13, 15]:
            for noise in [
                0.0001,
                0.0002,
                0.0003,
                0.0005,
                0.0008,
                0.001,
                0.002,
                0.003,
                0.005,
                0.008,
                0.01,
            ]:
                for gate_set in ['cx']:
                    rounds = diam * 3
                    noisy_circuit = make_noisy_heavy_hex_circuit(
                        diam=diam,
                        time_boundary_basis=basis,
                        rounds=rounds,
                        noise=noise,
                        gate_set=gate_set,
                    )

                    # Verify workable
                    noisy_circuit.detector_error_model(decompose_errors=True)

                    path = circuits_dir / f'd={diam},p={noise},b={basis},g={gate_set},r={rounds}.stim'
                    with open(path, 'w') as f:
                        print(noisy_circuit, file=f)
                    print("wrote", path)



if __name__ == '__main__':
    main()
