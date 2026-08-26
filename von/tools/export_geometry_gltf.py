#!/usr/bin/env python3
"""Convert a raw OBJ geometry export into a self-contained glTF 2.0 file."""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("obj", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    vertices: list[tuple[float, float, float]] = []
    indices: list[int] = []
    for line in args.obj.read_text().splitlines():
        if line.startswith("v "):
            _, x, y, z = line.split()
            vertices.append((float(x), float(y), float(z)))
        elif line.startswith("f "):
            indices.extend(int(part.split("/")[0]) - 1 for part in line.split()[1:])

    position_data = b"".join(struct.pack("<3f", *vertex) for vertex in vertices)
    index_data = b"".join(struct.pack("<I", index) for index in indices)
    buffer_data = position_data + index_data
    encoded = base64.b64encode(buffer_data).decode("ascii")
    minimum = [min(vertex[i] for vertex in vertices) for i in range(3)]
    maximum = [max(vertex[i] for vertex in vertices) for i in range(3)]

    document = {
        "asset": {"version": "2.0", "generator": "von export_geometry_gltf.py"},
        "scene": 0,
        "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": args.obj.stem}],
        "meshes": [{"name": args.obj.stem, "primitives": [{
            "attributes": {"POSITION": 0},
            "indices": 1,
            "mode": 4,
        }]}],
        "buffers": [{"byteLength": len(buffer_data),
                     "uri": "data:application/octet-stream;base64," + encoded}],
        "bufferViews": [
            {"buffer": 0, "byteOffset": 0, "byteLength": len(position_data),
             "target": 34962},
            {"buffer": 0, "byteOffset": len(position_data), "byteLength": len(index_data),
             "target": 34963},
        ],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(vertices),
             "type": "VEC3", "min": minimum, "max": maximum},
            {"bufferView": 1, "componentType": 5125, "count": len(indices),
             "type": "SCALAR"},
        ],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(vertices)} vertices and {len(indices) // 3} triangles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
