import base64
import collections
import dataclasses
import random
import sys
from typing import Tuple, Dict, List, Set, Optional, Union, Iterable

import stim

PITCH = 32
DIAM = 32
RAD = DIAM / 2
NOISY_GATES = {"X_ERROR", "Y_ERROR", "Z_ERROR", "E", "ELSE_CORRELATED_ERROR", "DEPOLARIZE1", "DEPOLARIZE2"}


def rand_color() -> str:
    color = '#'
    for _ in range(6):
        color += "0123456789abcdef"[random.randint(0, 15)]
    return color


MEASUREMENT_NAMES = {"M", "MX", "MY", "MR", "MRX", "MRY"}


@dataclasses.dataclass
class GateStyle:
    label: str
    fill_color: str
    text_color: str


def _init_gate_box_labels() -> Dict[str, GateStyle]:
    result = {'I': GateStyle(label='I', fill_color='white', text_color='gray')}
    for name in ["X", "Y", "Z"]:
        result[name] = GateStyle(label=name, fill_color='white', text_color='black')
    for name in ["R", "M", "RX", "RY", "MX", "MY", "MR", "MRX", "MRY"]:
        result[name] = GateStyle(label=name, fill_color='black', text_color='white')
    for key in ["H", "H_YZ", "H_XY", "S", "SQRT_X", "SQRT_Y", "S_DAG", "SQRT_X_DAG", "SQRT_Y_DAG"]:
        name = key.replace("SQRT_", "√")
        name = name.replace("_DAG", "⁻¹")
        a, b = name.split("_") if "_" in name else (name, "")
        result[key] = GateStyle(label=a + b.lower(), fill_color='yellow', text_color='black')
    for name in ["C_XYZ", "C_ZYX"]:
        result[name] = GateStyle(label=name[0] + name[2:].lower(), fill_color='teal', text_color='black')
    return result


GATE_BOX_LABELS = _init_gate_box_labels()
TWO_QUBIT_GATE_STYLES = {
    "CX": ("Z", "X"),
    "CY": ("Z", "Y"),
    "CZ": ("Z", "Z"),
    "XCX": ("X", "X"),
    "XCY": ("X", "Y"),
    "XCZ": ("X", "Z"),
    "YCX": ("Y", "X"),
    "YCY": ("Y", "Y"),
    "YCZ": ("Y", "Z"),
    "ISWAP": ("ISWAP", "ISWAP"),
    "ISWAP_DAG": ("ISWAP", "ISWAP"),
    "SWAP": ("SWAP", "SWAP"),
}


def tag_str(tag, *, content: Union[bool, str] = False, **kwargs) -> str:
    parts = [f"<{tag}"]
    for k, v in kwargs.items():
        parts.append(f"{k.replace('_', '-')}={str(v)!r}")
    instr = " ".join(parts)
    if not content:
        instr += " />"
    elif isinstance(content, str):
        instr += f">{content}</{tag}>"
    elif content is True:
        instr += ">"
    else:
        raise NotImplementedError(repr(content))

    return instr


class _SvgLayer:
    def __init__(self):
        self.svg_instructions: List[str] = []
        self.q2i_dict: Dict[int, Tuple[float, float]] = {}
        self.used_indices: Set[int] = set()
        self.used_positions: Set[Tuple[float, float]] = set()
        self.measurement_positions: Dict[int, Tuple[float, float]] = {}

    def add(self, tag, *, content: Union[bool, str] = False, **kwargs) -> None:
        self.svg_instructions.append("    " + tag_str(tag, content=content, **kwargs))

    def bounds(self) -> Tuple[float, float, float, float]:
        min_y = min(e for _, e in self.used_positions)
        max_y = max(e for _, e in self.used_positions)
        min_x = min(e for e, _ in self.used_positions)
        max_x = max(e for e, _ in self.used_positions)
        min_x -= PITCH
        min_y -= PITCH
        max_x += PITCH
        max_y += PITCH
        return min_x, min_y, max_x, max_y

    def add_idles(self, all_used_positions: Set[Tuple[float, float]]):
        for x, y in all_used_positions - self.used_positions:
            self.add("circle", cx=x, cy=y, r=5, fill="gray", stroke="black")
        self.used_positions |= all_used_positions
        min_x, min_y, max_x, max_y = self.bounds()
        xs = {e for e, _ in self.used_positions}
        ys = {e for _, e in self.used_positions}
        for x in xs:
            x2 = x
            x2 /= PITCH
            if x2 == int(x2):
                x2 = int(x2)
            self.add("text",
                     x=x,
                     y=max_y - 5,
                     fill="black",
                     content=str(x2),
                     text_anchor="middle",
                     dominant_baseline="auto",
                     font_size=24)
        for y in ys:
            y2 = y
            y2 /= PITCH
            if y2 == int(y2):
                y2 = int(y2)
            self.add("text",
                     x=min_x + 5,
                     y=y,
                     fill="black",
                     content=str(y2),
                     text_anchor="left",
                     alignment_baseline="middle",
                     font_size=24)

    def svg(self,
            *,
            html_id: Optional[str] = None,
            as_img_with_data_uri: bool = False,
            width: int,
            height: int) -> str:
        min_x, min_y, max_x, max_y = self.bounds()
        kwargs = {} if html_id is None or as_img_with_data_uri else {'id': html_id}
        svg = "\n".join([
            tag_str("svg",
                    xmlns="http://www.w3.org/2000/svg",
                    viewBox=f"{min_x} {min_y} {max_x - min_x} {max_y - min_y}",
                    content=True,
                    **kwargs),
            *self.svg_instructions,
            "</svg>",
        ])
        if as_img_with_data_uri:
            kwargs = {} if html_id is None else {'id': html_id}
            svg = tag_str("img",
                          width=width,
                          height=height,
                          **kwargs,
                          src="data:image/svg+xml;base64," + base64.standard_b64encode(svg.encode('utf-8')).decode('utf-8'))
            svg = svg.replace("/>", ">")
        return svg


class _SvgState:
    def __init__(self):
        self.layers: List[_SvgLayer] = [_SvgLayer()]
        self.coord_shift: List[int] = [0, 0]
        self.measurement_layer_indices: List[int] = []
        self.detector_index = 0
        self.detector_coords = {}
        self.measurement_marks = collections.Counter()
        self.highlighted_detectors = set()
        self.highlighted_errors: List[Tuple[int, int, str]] = []
        self.noted_errors: List[Tuple[int, int, str]] = []

    def tick(self) -> None:
        self.layers.append(_SvgLayer())
        self.layers[-1].q2i_dict = dict(self.layers[-2].q2i_dict)

    def q2i(self, i: int) -> Tuple[float, float]:
        x, y = self.layers[-1].q2i_dict.setdefault(i, (i, 0))
        pt = x * PITCH, y * PITCH
        self.layers[-1].used_indices.add(i)
        self.layers[-1].used_positions.add(pt)
        return pt

    def add(self, tag, *, content="", **kwargs) -> None:
        self.layers[-1].add(tag, content=content, **kwargs)

    def add_box(self, x: float, y: float, text: str, *, fill="white", text_color="black"):
        self.add("rect", x=x - RAD, y=y - RAD, width=DIAM, height=DIAM, fill=fill, stroke="black")
        self.add("text",
                 x=x,
                 y=y,
                 fill=text_color,
                 content=text,
                 font_size=32 if len(text) == 1 else 24 if len(text) == 2 else 18,
                 text_anchor="middle",
                 alignment_baseline="central")

    def add_measurement(self, target: stim.GateTarget) -> None:
        assert target.is_qubit_target or target.is_x_target or target.is_y_target or target.is_z_target
        m_index = len(self.measurement_layer_indices)
        self.measurement_layer_indices.append(len(self.layers) - 1)
        self.layers[-1].measurement_positions[m_index] = self.q2i(target.value)

    def mark_measurements(self, targets: List[stim.GateTarget], obs_index: Optional[int] = None) -> None:
        if obs_index is None:
            name = f"D{self.detector_index}"
            # if self.detector_index in self.detector_coords:
            #     name += str(self.detector_coords[self.detector_index])
            color = "black"
            if self.detector_index in self.highlighted_detectors:
                color = "#FF8000"
            self.detector_index += 1
        else:
            color = "blue"
            name = f"L{obs_index}"
        for t in targets:
            m_index = len(self.measurement_layer_indices) + t.value
            if m_index < 0:
                print("Attempted to mark a measurement before the beginning of time.\n"
                      "Skipping this mark.", file=sys.stderr)
                continue
            assert m_index >= 0, m_index
            assert t.is_measurement_record_target
            layer = self.layers[self.measurement_layer_indices[m_index]]
            x, y = layer.measurement_positions[m_index]
            if color == "#FF8000":
                layer.add("rect", x=x - RAD, y=y - RAD, width=DIAM, height=DIAM, fill=color, stroke="black")
            x += RAD + 1
            y -= RAD
            y += self.measurement_marks[m_index] * 15
            self.measurement_marks[m_index] += 1
            layer.add("text",
                      x=x,
                      y=y,
                      fill=color,
                      content=name,
                      text_anchor="left",
                      alignment_baseline="hanging",
                      font_size=16)


def _draw_endpoint(x: float, y: float, style: str, *, out: _SvgState) -> None:
    add = out.add
    if style == "X":
        add("circle", cx=x, cy=y, r=RAD, stroke="black", fill="white")
        add("line", x1=x - RAD, x2=x + RAD, y1=y, y2=y, stroke="black")
        add("line", x1=x, x2=x, y1=y - RAD, y2=y + RAD, stroke="black")
    elif style == "Y":
        s = 0.5**0.5
        add("circle", cx=x, cy=y, r=RAD, stroke="black", fill="white")
        add("line", x1=x, x2=x, y1=y, y2=y + RAD, stroke="black")
        add("line", x1=x, x2=x - RAD * s, y1=y, y2=y - RAD * s, stroke="black")
        add("line", x1=x, x2=x + RAD * s, y1=y, y2=y - RAD * s, stroke="black")
    elif style == "Z":
        add("circle", cx=x, cy=y, r=RAD, fill="black")
    elif style == "SWAP":
        r = RAD / 3
        add("line", x1=x - r, x2=x + r, y1=y - r, y2=y + r, stroke="black")
        add("line", x1=x - r, x2=x + r, y1=y + r, y2=y - r, stroke="black")
    elif style == "ISWAP":
        r = RAD
        add("circle", cx=x, cy=y, r=RAD / 2, fill="black")
        add("line", x1=x - r, x2=x + r, y1=y - r, y2=y + r, stroke="black")
        add("line", x1=x - r, x2=x + r, y1=y + r, y2=y - r, stroke="black")
    else:
        raise NotImplementedError(style)


def _draw_2q(instruction: stim.CircuitInstruction, *, out: _SvgState) -> None:
    style1, style2 = TWO_QUBIT_GATE_STYLES[instruction.name]
    targets = instruction.targets_copy()
    add = out.add
    q2i = out.q2i

    assert len(targets) % 2 == 0
    for k in range(0, len(targets), 2):
        t1 = targets[k]
        t2 = targets[k + 1]
        if t1.is_measurement_record_target or t2.is_measurement_record_target:
            if t1.is_qubit_target:
                t = t1.value
            elif t2.is_qubit_target:
                t = t2.value
            else:
                continue
            out.highlighted_errors.append((t, len(out.layers) - 1, 'C'))
            continue
        assert t1.is_qubit_target
        assert t2.is_qubit_target
        x1, y1 = q2i(t1.value)
        x2, y2 = q2i(t2.value)
        add("line", x1=x1, x2=x2, y1=y1, y2=y2, stroke="black")
        _draw_endpoint(x1, y1, style1, out=out)
        _draw_endpoint(x2, y2, style2, out=out)


def _draw_mpp(instruction: stim.CircuitInstruction, *, out: _SvgState) -> None:
    targets = instruction.targets_copy()
    add = out.add
    add_box = out.add_box
    q2i = out.q2i

    chunks = []
    start = 0
    end = 1
    while start < len(targets):
        while end < len(targets) and targets[end].is_combiner:
            end += 2
        chunks.append(targets[start:end:2])
        start = end
        end = start + 1
    for chunk in chunks:
        out.add_measurement(chunk[0])
        tx, ty = 0, 0
        for t in chunk:
            x, y = q2i(t.value)
            tx += x
            ty += y
        tx /= len(chunk)
        ty /= len(chunk)
        color = rand_color()
        no_text = False
        if all(t.is_x_target for t in chunk):
            color = '#FF8080'
            no_text = True
        if all(t.is_y_target for t in chunk):
            color = '#80FF80'
            no_text = True
        if all(t.is_z_target for t in chunk):
            color = '#8080FF'
            no_text = True
        for t in chunk:
            x, y = q2i(t.value)
            add("line", x1=x, x2=tx, y1=y, y2=ty, stroke=color, stroke_width=8)
        for k, c in enumerate(chunk):
            if c.is_x_target:
                text = "PX"
            elif c.is_y_target:
                text = "PY"
            elif c.is_z_target:
                text = "PZ"
            else:
                raise NotImplementedError(repr(c))
            x, y = q2i(c.value)
            add_box(x * 0.9 + tx * 0.1, y * 0.9 + ty * 0.1, text * (1 - int(no_text)), fill=color)


def _draw_1q(instruction: stim.CircuitInstruction, *, out: _SvgState):
    targets = instruction.targets_copy()
    if instruction.name in MEASUREMENT_NAMES:
        for t in targets:
            out.add_measurement(t)
    for t in targets:
        assert t.is_qubit_target
        x, y = out.q2i(t.value)
        style = GATE_BOX_LABELS[instruction.name]
        out.add_box(x, y, style.label, fill=style.fill_color, text_color=style.text_color)


def _stim_circuit_to_svg_helper(circuit: stim.Circuit, state: _SvgState) -> None:
    for instruction in circuit:
        if isinstance(instruction, stim.CircuitRepeatBlock):
            body = instruction.body_copy()
            for _ in range(instruction.repeat_count):
                _stim_circuit_to_svg_helper(body, state)
        elif isinstance(instruction, stim.CircuitInstruction):
            targets: List[stim.GateTarget] = instruction.targets_copy()
            if instruction.name == "QUBIT_COORDS":
                pos = instruction.gate_args_copy()
                for t in instruction.targets_copy():
                    assert t.is_qubit_target
                    if len(pos) == 1:
                        pos = (pos[0], 0)
                    state.layers[-1].q2i_dict[t.value] = (pos[0] + state.coord_shift[0], pos[1] + state.coord_shift[1])
            elif instruction.name == "SHIFT_COORDS":
                pos = instruction.gate_args_copy()
                if len(pos) >= 1:
                    state.coord_shift[0] += pos[0]
                if len(pos) >= 2:
                    state.coord_shift[1] += pos[1]
            elif instruction.name in GATE_BOX_LABELS:
                _draw_1q(instruction, out=state)
            elif instruction.name in TWO_QUBIT_GATE_STYLES:
                _draw_2q(instruction, out=state)
            elif instruction.name == "TICK":
                state.tick()
            elif instruction.name == "MPP":
                _draw_mpp(instruction, out=state)
            elif instruction.name == 'DETECTOR':
                state.mark_measurements(targets, obs_index=None)
            elif instruction.name == 'OBSERVABLE_INCLUDE':
                state.mark_measurements(targets, obs_index=int(instruction.gate_args_copy()[0]))
            elif instruction.name in NOISY_GATES:
                for t in instruction.targets_copy():
                    state.noted_errors.append((t.value, len(state.layers) - 1, 'E'))
            else:
                raise NotImplementedError(repr(instruction))
        else:
            raise NotImplementedError(repr(instruction))


def stim_circuit_html_viewer(circuit: stim.Circuit,
                             *,
                             width: int = 500,
                             height: int = 500,
                             known_error: Optional[Iterable[stim.ExplainedError]] = None) -> str:
    state = _SvgState()
    state.detector_coords = circuit.get_detector_coordinates()
    if known_error is None:
        # noinspection PyBroadException
        try:
            known_error = circuit.shortest_graphlike_error(
                ignore_ungraphlike_errors=True,
                canonicalize_circuit_errors=True,
            )
        except Exception:
            pass
    if known_error is not None:
        for product in known_error:
            loc = next(iter(product.circuit_error_locations))
            for flipped in loc.flipped_pauli_product:
                if flipped.gate_target.is_x_target:
                    b = 'X'
                elif flipped.gate_target.is_y_target:
                    b = 'Y'
                elif flipped.gate_target.is_z_target:
                    b = 'Z'
                else:
                    raise NotImplementedError(repr(loc))
                state.highlighted_errors.append((flipped.gate_target.value, loc.tick_offset, b))
            for term in product.dem_error_terms:
                target = term.dem_target
                if target.is_relative_detector_id():
                    state.highlighted_detectors.add(target.val)

    _stim_circuit_to_svg_helper(circuit, state)
    all_pos = {pt for layer in state.layers for pt in layer.used_positions}
    while state.layers and not state.layers[-1].svg_instructions:
        state.layers.pop()
    for layer in state.layers:
        layer.add_idles(all_pos)

    for qubit, time, basis in state.highlighted_errors:
        layer = state.layers[time]
        x, y = state.q2i(qubit)
        layer.add("text",
                  x=x,
                  y=y,
                  fill='yellow' if basis == 'C' else 'red',
                  content=basis,
                  text_anchor="middle",
                  dominant_baseline="middle",
                  font_size=64)
    for qubit, time, basis in set(state.noted_errors):
        layer = state.layers[time]
        x, y = state.q2i(qubit)
        layer.add("text",
                  x=x - RAD,
                  y=y,
                  fill="red",
                  content=basis,
                  text_anchor="end",
                  dominant_baseline="middle",
                  font_size=12)

    svg_image_tags = []
    for k, layer in enumerate(state.layers):
        svg = layer.svg(html_id=f"layer{k}", width=width, height=height)
        data = base64.standard_b64encode(svg.encode('utf-8')).decode('utf-8')
        svg_image_tags.append(
            f'<img style="max-width: 95%; max-height: 95%; display: none" '
            f'id=layer{k} '
            f'src="data:image/svg+xml;base64,{data}" />'
        )
    all_svg_image_tags = '\n'.join(svg_image_tags)

    flattened = circuit.flattened()
    circuit_coords = [str(inst) for inst in flattened if inst.name == "QUBIT_COORDS"]
    circuit_rest = [str(inst) for inst in flattened if inst.name != "QUBIT_COORDS"]

    escaped = ';'.join(circuit_coords + circuit_rest).replace(' ', '_')

    jetbrains_local_server_crumble_url = f"""http://localhost:63342/crumble/crumble.html#circuit={escaped}"""

    return (
            f"""<div id="step">Loading...</div>
    <button id="btnPrev">Previous Layer (hotkey: a)</button>
    <button id="btnNext">Next Layer (hotkey: d)</button>
    <a href="{jetbrains_local_server_crumble_url}">Open in Crumble</a>
    <div id="viewer" style="border: 1px solid black; margin-bottom: 50px; width: {width}px; 
             resize: both; overflow: auto">
        """
            + all_svg_image_tags
            + """
</div>
<script>
    let layer_index = 0;
    let layers = [];
    while (true) {
        let svg = document.getElementById('layer' + layers.length);
        if (svg === null) {
            break;
        }
        layers.push(svg);
    }

    function handleLayerIndexChange() {
        if (layer_index < 0) {
            layer_index = 0;
        }
        if (layer_index >= layers.length) {
            layer_index = layers.length - 1;
        }

        let layerName = layer_index + 1;
        document.getElementById('step').innerHTML = "Layer: " + layerName + "/" + layers.length;
        for (let k = 0; k < layers.length; k++) {
            let svg = layers[k];
            if (layer_index === k) {
                svg.style.display = "";
            } else {
                svg.style.display = "none";
            }
        }
    }
    document.getElementById("btnPrev").addEventListener("click", ev => {
        layer_index -= 1;
        handleLayerIndexChange();
    });
    document.getElementById("btnNext").addEventListener("click", ev => {
        layer_index += 1;
        handleLayerIndexChange();
    });
    document.addEventListener('keydown', ev => {
        if (ev.code == "KeyA" && !ev.getModifierState("Control")) {
            layer_index -= 1;
            ev.preventDefault();
            handleLayerIndexChange();
        } else if (ev.code == "KeyD") {
            layer_index += 1;
            ev.preventDefault();
            handleLayerIndexChange();
        }
    });

    handleLayerIndexChange();
</script>"""
    )
