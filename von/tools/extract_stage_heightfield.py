#!/usr/bin/env python3
"""Rasterise a terrain arena into a height grid and a glTF mesh.

GREEN HILLS (stage ordinal 3) is rolling terrain: its arena statics are many
mid-size, non-flat meshes rather than the discrete blocks the flat stages use.
This tool samples the top surface of those meshes onto an NxN grid over the
+/-half play area and emits (a) a heightfield glTF the renderer can load as
`stage_03_arena.gltf` and (b) the C array the kernel embeds for ground height.

The OBA list below is the GREEN HILLS arena set observed in the binding probe
(`von/i960/stage-arena-binding.md`) filtered to ground-like meshes (not walls,
floor or backdrop). Re-run with the geometry ROM:

    python3 von/tools/extract_stage_heightfield.py \
        --output /path/to/von-godot/assets/generated/arena/stage_03_arena.gltf
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

from export_geometry_animation_gltf import parse_mesh

GREEN_HILLS_OBAS = [
    0x00808A79, 0x00808C88, 0x00808E01, 0x00808FCA, 0x008090CB, 0x00809294,
    0x0080936D, 0x008095F4, 0x00809777, 0x008098DC, 0x008099BF, 0x00809B38,
    0x00809C6B, 0x00809F10, 0x0080A0CF, 0x0080A1D0, 0x0080A259, 0x0080A346,
]


def sample(rom: bytes, obas: list[int], n: int, half: float) -> list[list[float]]:
    grid = [[0.0] * n for _ in range(n)]
    for oba in obas:
        vertices, indices = parse_mesh(rom, oba, 0x4000)
        if not vertices:
            continue
        for k in range(0, len(indices), 3):
            a, b, c = vertices[indices[k]], vertices[indices[k + 1]], vertices[indices[k + 2]]
            for gj in range(n):
                gz = -half + gj * (2 * half / (n - 1))
                for gi in range(n):
                    gx = -half + gi * (2 * half / (n - 1))
                    denom = (b[2] - c[2]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[2] - c[2])
                    if abs(denom) < 1e-9:
                        continue
                    w0 = ((b[2] - c[2]) * (gx - c[0]) + (c[0] - b[0]) * (gz - c[2])) / denom
                    w1 = ((c[2] - a[2]) * (gx - c[0]) + (a[0] - c[0]) * (gz - c[2])) / denom
                    w2 = 1 - w0 - w1
                    if w0 >= -0.001 and w1 >= -0.001 and w2 >= -0.001:
                        grid[gj][gi] = max(grid[gj][gi], w0 * a[1] + w1 * b[1] + w2 * c[1])
    return grid


def write_gltf(path: Path, grid: list[list[float]], half: float) -> None:
    n = len(grid)
    verts = [(-half + gi * (2 * half / (n - 1)), grid[gj][gi],
              -half + gj * (2 * half / (n - 1)))
             for gj in range(n) for gi in range(n)]
    indices: list[int] = []
    for gj in range(n - 1):
        for gi in range(n - 1):
            a = gj * n + gi
            indices += [a, a + n, a + 1, a + 1, a + n, a + n + 1]
    pos = b"".join(struct.pack("<3f", *v) for v in verts)
    idx = b"".join(struct.pack("<I", i) for i in indices)
    blob = pos + idx
    document = {
        "asset": {"version": "2.0", "generator": "extract_stage_heightfield"},
        "scene": 0,
        "scenes": [{"name": "green_hills_terrain", "nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "slot_000_oba_0080ffff",
                   "extras": {"heightfield": {"n": n, "half": half, "terrain": True}}}],
        "meshes": [{"name": "green_hills_terrain",
                    "primitives": [{"attributes": {"POSITION": 0}, "indices": 1, "mode": 4}]}],
        "buffers": [{"byteLength": len(blob),
                     "uri": "data:application/octet-stream;base64," +
                            base64.b64encode(blob).decode("ascii")}],
        "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pos), "target": 34962},
                        {"buffer": 0, "byteOffset": len(pos), "byteLength": len(idx), "target": 34963}],
        "accessors": [
            {"bufferView": 0, "componentType": 5126, "count": len(verts), "type": "VEC3",
             "min": [min(v[0] for v in verts), min(v[1] for v in verts), min(v[2] for v in verts)],
             "max": [max(v[0] for v in verts), max(v[1] for v in verts), max(v[2] for v in verts)]},
            {"bufferView": 1, "componentType": 5125, "count": len(indices), "type": "SCALAR"},
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n")


def print_c_array(grid: list[list[float]]) -> None:
    n = len(grid)
    print(f"static const float RV_TERRAIN_GREEN_HILLS[{n * n}] = {{")
    for row in grid:
        print("    " + ", ".join(f"{v:.1f}f" for v in row) + ",")
    print("};")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--grid", type=int, default=17)
    parser.add_argument("--half", type=float, default=320.0)
    parser.add_argument("--c-array", action="store_true")
    args = parser.parse_args()
    rom = args.rom.read_bytes()
    grid = sample(rom, GREEN_HILLS_OBAS, args.grid, args.half)
    write_gltf(args.output, grid, args.half)
    print(f"wrote {args.output} ({args.grid}x{args.grid})")
    if args.c_array:
        print_c_array(grid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
