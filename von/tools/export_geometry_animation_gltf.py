#!/usr/bin/env python3
"""Export event-ordered polygon objects and matrices as an animated glTF."""

from __future__ import annotations

import argparse
import base64
import json
import math
import re
import struct
from pathlib import Path


OBJECT = re.compile(
    r"vonj_geometry_object: seq=(\d+) time=([0-9.]+) tpa=([0-9a-f]+) "
    r"tha=([0-9a-f]+) oba=([0-9a-f]+) count=([0-9a-f]+) mode=(\d+) source=([^ ]+)"
)
MATRIX = re.compile(
    r"vonj_geometry_matrix: seq=(\d+) time=([0-9.]+) "
    r"m=([^ ]+) t=([^ ]+)"
)


def parse_mesh(rom: bytes, oba: int, window: int = 0x4000):
    start = (oba & 0x3fffff) * 4
    values = [int.from_bytes(rom[pos:pos + 4], "little")
              for pos in range(start, min(start + window * 4, len(rom)), 4)]
    cursor = 0
    vertices = []
    indices = []

    def point():
        nonlocal cursor
        result = tuple(struct.unpack("<f", value.to_bytes(4, "little"))[0]
                       for value in values[cursor:cursor + 3])
        cursor += 3
        return result

    p0 = point()
    p1 = point()
    while cursor < len(values):
        attr = values[cursor]
        cursor += 1
        if not (attr & 3) or cursor + 6 > len(values):
            break
        cursor += 3
        p2 = point()
        if attr & 1:
            p3 = point()
        else:
            cursor += 3
            p3 = p2
        base = len(vertices)
        vertices.extend((p0, p1, p2, p3))
        if attr & 1:
            indices.extend((base, base + 1, base + 2, base, base + 2, base + 3))
        else:
            indices.extend((base, base + 1, base + 2))
        link = (attr >> 8) & 3
        if link in (0, 2):
            p0, p1 = p2, p3
        elif link == 1:
            p1 = p2
        else:
            p0 = p3
    return vertices, indices


def transform_trs(matrix: tuple[float, ...]):
    columns = ((matrix[0], matrix[1], matrix[2]),
               (matrix[3], matrix[4], matrix[5]),
               (matrix[6], matrix[7], matrix[8]))
    scale = [math.sqrt(sum(value * value for value in column)) for column in columns]
    r = [[columns[col][row] / scale[col] if scale[col] else float(row == col)
          for col in range(3)] for row in range(3)]
    trace = r[0][0] + r[1][1] + r[2][2]
    if trace > 0:
        s = math.sqrt(trace + 1.0) * 2
        q = ((r[2][1] - r[1][2]) / s, (r[0][2] - r[2][0]) / s,
             (r[1][0] - r[0][1]) / s, 0.25 * s)
    elif r[0][0] > r[1][1] and r[0][0] > r[2][2]:
        s = math.sqrt(1.0 + r[0][0] - r[1][1] - r[2][2]) * 2
        q = (0.25 * s, (r[0][1] + r[1][0]) / s, (r[0][2] + r[2][0]) / s,
             (r[2][1] - r[1][2]) / s)
    elif r[1][1] > r[2][2]:
        s = math.sqrt(1.0 + r[1][1] - r[0][0] - r[2][2]) * 2
        q = ((r[0][1] + r[1][0]) / s, 0.25 * s, (r[1][2] + r[2][1]) / s,
             (r[0][2] - r[2][0]) / s)
    else:
        s = math.sqrt(1.0 + r[2][2] - r[0][0] - r[1][1]) * 2
        q = ((r[0][2] + r[2][0]) / s, (r[1][2] + r[2][1]) / s,
             0.25 * s, (r[1][0] - r[0][1]) / s)
    norm = math.sqrt(sum(component * component for component in q))
    if norm == 0.0:
        raise ValueError("zero-length rotation quaternion")
    return tuple(component / norm for component in q), tuple(scale)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path,
                        default=Path("von/build/disasm/vonj-animation-seq.trace"))
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output", type=Path,
                        default=Path("von/build/disasm/player-select-animation.gltf"))
    args = parser.parse_args()

    events = []
    for line in args.trace.read_text().splitlines():
        match = OBJECT.search(line)
        if match:
            events.append((int(match[1]), "object", float(match[2]), int(match[5], 16)))
            continue
        match = MATRIX.search(line)
        if match:
            matrix = tuple(float(value) for value in match[3].split(","))
            translation = tuple(float(value) for value in match[4].split(","))
            events.append((int(match[1]), "matrix", float(match[2]), matrix + translation))
    events.sort()

    frames: dict[float, list[tuple[int, tuple[float, ...]]]] = {}
    current = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
               0.0, 0.0, 0.0)
    for _, kind, time, value in events:
        if kind == "matrix":
            current = value
        else:
            frames.setdefault(time, []).append((value, current))
    frames = {time: objects for time, objects in frames.items() if len(objects) == 40}
    times = sorted(frames)
    if not times:
        raise SystemExit("no complete 40-object frames found")
    slots = [oba for oba, _ in frames[times[0]]]
    if any([oba for oba, _ in frames[time]] != slots for time in times):
        raise SystemExit("object order changed between frames")

    blob = bytearray()
    views = []
    accessors = []
    meshes = []
    mesh_by_oba = {}
    rom = args.rom.read_bytes()

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    for oba in slots:
        if oba not in mesh_by_oba:
            vertices, indices = parse_mesh(rom, oba)
            positions = b"".join(struct.pack("<3f", *vertex) for vertex in vertices)
            index_data = b"".join(struct.pack("<I", index) for index in indices)
            pv = add_blob(positions, 34962)
            iv = add_blob(index_data, 34963)
            minimum = [min(vertex[i] for vertex in vertices) for i in range(3)]
            maximum = [max(vertex[i] for vertex in vertices) for i in range(3)]
            accessors.extend([
                {"bufferView": pv, "componentType": 5126, "count": len(vertices),
                 "type": "VEC3", "min": minimum, "max": maximum},
                {"bufferView": iv, "componentType": 5125, "count": len(indices),
                 "type": "SCALAR"},
            ])
            mesh_by_oba[oba] = len(meshes)
            meshes.append({"name": f"oba_{oba:08x}", "primitives": [{
                "attributes": {"POSITION": len(accessors) - 2},
                "indices": len(accessors) - 1, "mode": 4,
            }]})

    node_count = len(slots)
    nodes = [{"mesh": mesh_by_oba[oba], "name": f"slot_{slot:02d}_oba_{oba:08x}"}
             for slot, oba in enumerate(slots)]
    input_view = add_blob(b"".join(struct.pack("<f", time - times[0]) for time in times))
    input_accessor = len(accessors)
    accessors.append({"bufferView": input_view, "componentType": 5126, "count": len(times),
                      "type": "SCALAR", "min": [0.0], "max": [times[-1] - times[0]]})
    channels = []
    samplers = []
    for slot in range(node_count):
        translations = b"".join(struct.pack("<3f", *frames[time][slot][1][9:12]) for time in times)
        rotations = b"".join(struct.pack("<4f", *transform_trs(frames[time][slot][1])[0]) for time in times)
        scales = b"".join(struct.pack("<3f", *transform_trs(frames[time][slot][1])[1]) for time in times)
        for path, data, accessor_type in (("translation", translations, "VEC3"),
                                          ("rotation", rotations, "VEC4"),
                                          ("scale", scales, "VEC3")):
            view = add_blob(data)
            accessor = len(accessors)
            accessors.append({"bufferView": view, "componentType": 5126,
                              "count": len(times), "type": accessor_type})
            sampler = len(samplers)
            samplers.append({"input": input_accessor, "output": accessor, "interpolation": "LINEAR"})
            channels.append({"sampler": sampler, "target": {"node": slot, "path": path}})

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_animation_gltf.py"},
        "scene": 0, "scenes": [{"nodes": list(range(node_count))}], "nodes": nodes,
        "meshes": meshes, "animations": [{"name": "player_select", "samplers": samplers,
                                           "channels": channels}],
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {node_count} nodes, {len(meshes)} meshes, and {len(times)} animation frames to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
