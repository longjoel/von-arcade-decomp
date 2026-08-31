#!/usr/bin/env python3
"""Export a polygon-ROM frame as a cumulative, triangle-by-triangle glTF animation."""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

from export_geometry_animation_gltf import parse_mesh, transform_trs
from export_geometry_frame_gltf import MATRIX, OBJECT


def select_geometry(trace: Path, requested_time: float | None, tolerance: float,
                    minimum: int, maximum_time: float | None):
    current = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0)
    frames: dict[float, list[tuple[int, tuple[float, ...], dict[str, int | str]]]] = {}
    for line in trace.read_text(errors="replace").splitlines():
        matrix = MATRIX.search(line)
        if matrix:
            current = tuple(float(value) for value in matrix[2].split(",")) + tuple(
                float(value) for value in matrix[3].split(",")
            )
            continue
        match = OBJECT.search(line)
        if not match or int(match[6]) != 3 or match[7] != "polygon-rom":
            continue
        time = float(match[1])
        frames.setdefault(time, []).append((int(match[4], 16), current, {
            "tpa": int(match[2], 16), "tha": int(match[3], 16),
            "count": int(match[5], 16), "mode": 3, "source": "polygon-rom",
        }))
    candidates = [(time, objects) for time, objects in frames.items()
                  if len(objects) >= minimum and (maximum_time is None or time <= maximum_time)]
    if not candidates:
        raise SystemExit("no polygon-ROM geometry frame met the requested bounds")
    if requested_time is None:
        return max(candidates, key=lambda item: item[0])
    selected = min(candidates, key=lambda item: abs(item[0] - requested_time))
    if abs(selected[0] - requested_time) > tolerance:
        raise SystemExit(f"no geometry frame within {tolerance:g}s of {requested_time:g}")
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--time", type=float)
    parser.add_argument("--max-time", type=float)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--max-triangles", type=int, default=3000,
                        help="cap output size; zero means no cap")
    parser.add_argument("--seconds", type=float, default=12.0,
                        help="duration of the cumulative reveal")
    args = parser.parse_args()
    if args.max_triangles < 0 or args.seconds <= 0.0:
        raise SystemExit("--max-triangles must be nonnegative and --seconds must be positive")

    selected_time, objects = select_geometry(
        args.trace, args.time, args.tolerance, args.min_objects, args.max_time
    )
    blob = bytearray()
    views: list[dict] = []
    accessors: list[dict] = []
    meshes: list[dict] = []
    nodes: list[dict] = []
    samplers: list[dict] = []
    channels: list[dict] = []

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view = {"buffer": 0, "byteOffset": offset, "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    def add_accessor(data: bytes, count: int, kind: str, target: int | None = None) -> int:
        view = add_blob(data, target)
        accessors.append({"bufferView": view, "componentType": 5126,
                          "count": count, "type": kind})
        return len(accessors) - 1

    rom = args.rom.read_bytes()
    triangle_records = []
    for oba, matrix, metadata in objects:
        vertices, indices = parse_mesh(rom, oba)
        for cursor in range(0, len(indices), 3):
            triangle_records.append((tuple(vertices[index] for index in indices[cursor:cursor + 3]),
                                     matrix, oba, metadata))
            if args.max_triangles and len(triangle_records) >= args.max_triangles:
                break
        if args.max_triangles and len(triangle_records) >= args.max_triangles:
            break
    if not triangle_records:
        raise SystemExit("selected geometry produced no triangles")

    for ordinal, (triangle, matrix, oba, metadata) in enumerate(triangle_records):
        position = add_accessor(b"".join(struct.pack("<3f", *vertex) for vertex in triangle),
                                3, "VEC3", 34962)
        index = add_blob(struct.pack("<3I", 0, 1, 2), 34963)
        accessors.append({"bufferView": index, "componentType": 5125, "count": 3, "type": "SCALAR"})
        meshes.append({"name": f"triangle_{ordinal:05d}_oba_{oba:08x}", "primitives": [{
            "attributes": {"POSITION": position}, "indices": len(accessors) - 1, "mode": 4,
        }]})
        rotation, scale = transform_trs(matrix)
        node = len(nodes)
        nodes.append({"mesh": len(meshes) - 1, "name": f"triangle_{ordinal:05d}_oba_{oba:08x}",
                      "translation": list(matrix[9:12]), "rotation": list(rotation),
                      "scale": [0.0, 0.0, 0.0],
                      "extras": {"trace_time": selected_time, "submission_index": ordinal,
                                 "geometry_object": metadata, "final_scale": list(scale)}})
        reveal = args.seconds * (ordinal + 1) / len(triangle_records)
        input_accessor = add_accessor(struct.pack("<2f", 0.0, reveal), 2, "SCALAR")
        accessors[input_accessor]["min"] = [0.0]
        accessors[input_accessor]["max"] = [reveal]
        output_accessor = add_accessor(struct.pack("<6f", 0.0, 0.0, 0.0, *scale), 2, "VEC3")
        samplers.append({"input": input_accessor, "output": output_accessor, "interpolation": "STEP"})
        channels.append({"sampler": len(samplers) - 1,
                         "target": {"node": node, "path": "scale"}})

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_triangle_build_gltf.py"},
        "scene": 0, "scenes": [{"name": f"triangle_build_{selected_time:.6f}",
                                    "nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes,
        "animations": [{"name": "triangle_submission_order", "samplers": samplers,
                        "channels": channels}],
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views, "accessors": accessors,
        "extras": {"trace_time": selected_time, "triangle_count": len(triangle_records),
                   "object_slots": len(objects), "geometry_filter": "mode=3 source=polygon-rom"},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(triangle_records)} triangle nodes from {len(objects)} polygon-ROM slots "
          f"at timestamp {selected_time:.6f} to {args.output}")


if __name__ == "__main__":
    raise SystemExit(main())
