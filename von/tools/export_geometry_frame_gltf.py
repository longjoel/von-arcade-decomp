#!/usr/bin/env python3
"""Export one timestamped geometry submission frame as an instanced glTF scene.

The animation exporter is deliberately strict about the 40-object player-select
layout.  Match cutscenes and arenas submit a larger, sometimes changing set of
objects, so this tool selects one timestamp and preserves every object slot and
its most recently traced transform.
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import struct
from pathlib import Path

from export_geometry_animation_gltf import parse_mesh, transform_trs


OBJECT = re.compile(
    r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+) "
    r"tpa=([0-9a-f]+) tha=([0-9a-f]+) oba=([0-9a-f]+) "
    r"count=([0-9a-f]+) mode=(\d+) source=([^ ]+)"
)
MATRIX = re.compile(
    r"vonj_geometry_matrix: (?:seq=\d+ )?time=([0-9.e+-]+) "
    r"m=([^ ]+) t=([^ ]+)"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time", type=float,
                        help="timestamp to select; defaults to the latest frame with a traced matrix")
    parser.add_argument("--max-time", type=float,
                        help="ignore frames after this timestamp during automatic selection")
    parser.add_argument("--tolerance", type=float, default=0.02,
                        help="maximum timestamp distance when --time is supplied")
    parser.add_argument("--window", type=int, default=0x4000)
    parser.add_argument("--min-objects", type=int, default=1,
                        help="minimum object submissions for automatic frame selection")
    args = parser.parse_args()

    current = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0,
               0.0, 0.0, 0.0)
    frames: dict[float, list[tuple[int, tuple[float, ...], dict[str, int | str]]]] = {}
    for line in args.trace.read_text().splitlines():
        matrix = MATRIX.search(line)
        if matrix:
            values = tuple(float(value) for value in matrix[2].split(","))
            translation = tuple(float(value) for value in matrix[3].split(","))
            current = values + translation
            continue
        match = OBJECT.search(line)
        if not match:
            continue
        time = float(match[1])
        metadata = {
            "tpa": int(match[2], 16),
            "tha": int(match[3], 16),
            "count": int(match[5], 16),
            "mode": int(match[6]),
            "source": match[7],
        }
        frames.setdefault(time, []).append((int(match[4], 16), current, metadata))

    candidates = sorted(
        ((time, objects) for time, objects in frames.items()
         if len(objects) >= args.min_objects and
         (args.max_time is None or time <= args.max_time)),
        key=lambda item: item[0],
    )
    if not candidates:
        raise SystemExit("no geometry frames met --min-objects")
    if args.time is None:
        selected_time, objects = candidates[-1]
    else:
        selected_time, objects = min(candidates, key=lambda item: abs(item[0] - args.time))
        if abs(selected_time - args.time) > args.tolerance:
            raise SystemExit(
                f"no frame within {args.tolerance:g}s of {args.time:g}; "
                f"nearest is {selected_time:g}"
            )

    rom = args.rom.read_bytes()
    blob = bytearray()
    views: list[dict[str, int]] = []
    accessors: list[dict[str, object]] = []
    meshes: list[dict[str, object]] = []
    mesh_by_oba: dict[int, int] = {}

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view: dict[str, int] = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    for oba, _, _ in objects:
        if oba in mesh_by_oba:
            continue
        vertices, indices = parse_mesh(rom, oba, args.window)
        if not vertices or not indices:
            raise SystemExit(f"object {oba:08x} produced no triangles")
        positions = b"".join(struct.pack("<3f", *vertex) for vertex in vertices)
        index_data = b"".join(struct.pack("<I", index) for index in indices)
        position_view = add_blob(positions, 34962)
        index_view = add_blob(index_data, 34963)
        minimum = [min(vertex[i] for vertex in vertices) for i in range(3)]
        maximum = [max(vertex[i] for vertex in vertices) for i in range(3)]
        position_accessor = len(accessors)
        accessors.extend([
            {"bufferView": position_view, "componentType": 5126, "count": len(vertices),
             "type": "VEC3", "min": minimum, "max": maximum},
            {"bufferView": index_view, "componentType": 5125, "count": len(indices),
             "type": "SCALAR"},
        ])
        mesh_by_oba[oba] = len(meshes)
        meshes.append({
            "name": f"oba_{oba:08x}",
            "primitives": [{
                "attributes": {"POSITION": position_accessor},
                "indices": position_accessor + 1,
                "mode": 4,
            }],
        })

    nodes = []
    for slot, (oba, matrix, metadata) in enumerate(objects):
        rotation, scale = transform_trs(matrix)
        nodes.append({
            "mesh": mesh_by_oba[oba],
            "name": f"slot_{slot:03d}_oba_{oba:08x}",
            "translation": list(matrix[9:12]),
            "rotation": list(rotation),
            "scale": list(scale),
            "extras": {"geometry_object": metadata, "trace_time": selected_time},
        })

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_frame_gltf.py"},
        "scene": 0,
        "scenes": [{"name": f"geometry_frame_{selected_time:.6f}",
                    "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views,
        "accessors": accessors,
        "extras": {"trace_time": selected_time, "object_slots": len(objects),
                   "unique_meshes": len(meshes)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(objects)} object slots, {len(meshes)} unique meshes, "
          f"and timestamp {selected_time:.6f} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
