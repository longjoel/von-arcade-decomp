#!/usr/bin/env python3
"""Dump a stage's arena geometry, collision boxes, and heightfield from ROM.

Inputs:
  --manifest  per-ordinal arena OBA lists (von/i960/stage-arena-obas.json,
              produced from the binding-probe traces)
  --rom       assembled polygon ROM (von/tools/extract_geometry_rom.py)

Outputs (into --output-dir):
  stage_<NN>_arena.gltf      every arena static as an instanced mesh at identity
                             (the decoder emits world-space vertices)
  stage_<NN>_boxes.json      render-measured collision boxes (low blocks)
  stage_<NN>_heightfield.json  top-surface height grid over +/-half
  stage_<NN>_summary.md      role table (floor / ground / wall / block / backdrop)

Classification is geometric:
  block   y in [-5,10], height in [8,100], footprint in [8,340], inside shell
  ground  y_max <= ground_max_y and footprint <= ground_max_footprint
The host stages the glTF; the kernel embeds the heightfield/boxes.
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
from pathlib import Path

from export_geometry_animation_gltf import parse_mesh


def load_obas(manifest: Path, stage: int) -> list[int]:
    data = json.loads(manifest.read_text())
    entries = data[str(stage)]
    return [int(e["oba"], 0) for e in entries]


def classify(oba: int, mn: list[float], mx: list[float]) -> str:
    sx, sy, sz = mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]
    footprint = max(sx, sz)
    if footprint > 1500:
        return "backdrop"
    if mn[1] <= -5 and sy >= 8:
        return "wall"
    if -5 <= mn[1] <= 10 and 8 <= sy <= 100 and 8 <= sx <= 200 and 8 <= sz <= 200:
        return "block"
    if sy <= 8 and footprint <= 1500:
        return "ground"
    return "structure"


def is_block(mn: list[float], mx: list[float], shell: float) -> bool:
    sx, sy, sz = mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]
    return (-5 <= mn[1] <= 10 and 8 <= sy <= 100 and 8 <= sx <= 200 and 8 <= sz <= 200
            and max(abs(mn[0]), abs(mx[0]), abs(mn[2]), abs(mx[2])) <= shell)


def is_ground(mn: list[float], mx: list[float], max_y: float, max_foot: float) -> bool:
    footprint = max(mx[0] - mn[0], mx[2] - mn[2])
    return mx[1] <= max_y and footprint <= max_foot


def rasterize(rom: bytes, obas: list[int], n: int, half: float,
              max_y: float, max_foot: float) -> list[list[float]]:
    grid: list[list[float | None]] = [[None] * n for _ in range(n)]
    for oba in obas:
        vertices, indices = parse_mesh(rom, oba, 0x4000)
        if not vertices:
            continue
        mn = [min(p[k] for p in vertices) for k in range(3)]
        mx = [max(p[k] for p in vertices) for k in range(3)]
        if classify(oba, mn, mx) == "block":
            continue
        if not is_ground(mn, mx, max_y, max_foot):
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
                        y = w0 * a[1] + w1 * b[1] + w2 * c[1]
                        if grid[gj][gi] is None or y > grid[gj][gi]:
                            grid[gj][gi] = y
    return [[0.0 if v is None else v for v in row] for row in grid]


def write_gltf(path: Path, rom: bytes, obas: list[int]) -> int:
    blob = bytearray()
    views: list[dict] = []
    accessors: list[dict] = []
    meshes: list[dict] = []
    nodes: list[dict] = []
    for slot, oba in enumerate(obas):
        vertices, indices = parse_mesh(rom, oba, 0x4000)
        if not vertices or not indices:
            continue
        pos = b"".join(struct.pack("<3f", *v) for v in vertices)
        idx = b"".join(struct.pack("<I", i) for i in indices)
        pos_off = len(blob); blob += pos
        idx_off = len(blob); blob += idx
        views.append({"buffer": 0, "byteOffset": pos_off, "byteLength": len(pos), "target": 34962})
        views.append({"buffer": 0, "byteOffset": idx_off, "byteLength": len(idx), "target": 34963})
        acc = len(accessors)
        accessors.append({"bufferView": len(views) - 2, "componentType": 5126, "count": len(vertices),
                          "type": "VEC3",
                          "min": [min(v[k] for v in vertices) for k in range(3)],
                          "max": [max(v[k] for v in vertices) for k in range(3)]})
        accessors.append({"bufferView": len(views) - 1, "componentType": 5125,
                          "count": len(indices), "type": "SCALAR"})
        meshes.append({"name": f"oba_{oba:08x}",
                       "primitives": [{"attributes": {"POSITION": acc}, "indices": acc + 1, "mode": 4}]})
        nodes.append({"mesh": len(meshes) - 1, "name": f"slot_{slot:03d}_oba_{oba:08x}"})
    document = {
        "asset": {"version": "2.0", "generator": "extract_stage_geometry.py"},
        "scene": 0,
        "scenes": [{"name": "arena", "nodes": list(range(len(nodes)))}],
        "nodes": nodes, "meshes": meshes, "accessors": accessors,
        "buffers": [{"byteLength": len(blob),
                     "uri": "data:application/octet-stream;base64," +
                            base64.b64encode(bytes(blob)).decode("ascii")}],
        "bufferViews": views,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, indent=2) + "\n")
    return len(nodes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=int, required=True)
    parser.add_argument("--rom", type=Path, default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--manifest", type=Path,
                        default=Path("von/i960/stage-arena-obas.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--grid", type=int, default=17)
    parser.add_argument("--half", type=float, default=320.0)
    parser.add_argument("--ground-max-y", type=float, default=80.0)
    parser.add_argument("--ground-max-footprint", type=float, default=1300.0)
    parser.add_argument("--no-gltf", action="store_true")
    args = parser.parse_args()

    rom = args.rom.read_bytes()
    obas = load_obas(args.manifest, args.stage)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    tag = f"stage_{args.stage:02d}"

    roles = {}
    boxes = []
    for oba in obas:
        vertices, _ = parse_mesh(rom, oba, 0x4000)
        if not vertices:
            continue
        mn = [min(p[k] for p in vertices) for k in range(3)]
        mx = [max(p[k] for p in vertices) for k in range(3)]
        role = classify(oba, mn, mx)
        roles[f"{oba:#010x}"] = role
        if is_block(mn, mx, args.half + 40.0):
            boxes.append({"oba": f"{oba:#010x}", "kind": 0,
                          "min": [round(v) for v in mn], "max": [round(v) for v in mx]})

    grid = rasterize(rom, obas, args.grid, args.half,
                     args.ground_max_y, args.ground_max_footprint)
    if not args.no_gltf:
        count = write_gltf(args.output_dir / f"{tag}_arena.gltf", rom, obas)
    else:
        count = 0
    (args.output_dir / f"{tag}_boxes.json").write_text(json.dumps(boxes, indent=2) + "\n")
    (args.output_dir / f"{tag}_heightfield.json").write_text(
        json.dumps({"n": args.grid, "half": args.half, "grid": grid}, indent=2) + "\n")
    summary = [f"# Stage {args.stage} arena", "",
               f"statics: {len(obas)} OBAs, {count} exported to glTF", "",
               "| OBA | role |", "| --- | --- |"]
    summary += [f"| {oba} | {role} |" for oba, role in sorted(roles.items())]
    summary += ["", f"blocks: {len(boxes)}", ""]
    (args.output_dir / f"{tag}_summary.md").write_text("\n".join(summary) + "\n")
    print(f"stage {args.stage}: {len(obas)} OBAs, {len(boxes)} blocks, "
          f"{sum(1 for r in roles.values() if r == 'ground')} ground meshes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
