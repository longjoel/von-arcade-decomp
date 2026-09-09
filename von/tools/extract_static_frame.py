#!/usr/bin/env python3
"""Extract a MAME-free static model frame from ROM part tables.

Pipeline (no MAME, no traces): decode [tpa, tha, oba] part records from
main_data with decode_model_part_table, decode each part's triangles from
the geometry ROM with parse_mesh, pose the parts, and emit glTF 2.0 in the
same document shape as export_geometry_frame_gltf.py.

Poses are the one thing traces used to supply. This tool offers identity
(exact decode output, best for verification) and distribute (parts spread
along X by index, viewable). Static per-frame matrices from motion tables
are a later slice; tpa/tha texture wiring is intentionally out of scope
(positions only).

Verification: per-OBA triangle soups are pose-independent, so the static
meshes must match the traced asset for the same table up to node
transforms (see test_extract_static_frame.py).
"""

from __future__ import annotations

import argparse
import base64
import json
import struct
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--offset", type=lambda value: int(value, 0), required=True,
                        help="main_data offset of the first part-table word")
    parser.add_argument("--words", type=int, required=True)
    parser.add_argument("--pose", choices=("identity", "distribute"),
                        default="identity")
    parser.add_argument("--spread", type=float, default=50.0,
                        help="X spacing per part under --pose distribute")
    parser.add_argument("--window", type=lambda value: int(value, 0),
                        default=0x4000)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()

    root = args.root.resolve()
    for label, path in (("ROM", args.rom), ("output", args.output)):
        resolved = (root / path).resolve() if not path.is_absolute() else path
        if root not in resolved.parents and resolved != root:
            raise SystemExit(f"{label} {path} escapes --root {root}")

    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from decode_model_part_table import load_main_data, decode_records
    from export_geometry_animation_gltf import parse_mesh

    rom = (root / args.rom).read_bytes()
    main_data = load_main_data(root / args.rom_dir)
    words = list(struct.unpack(f"<{args.words}I",
                               main_data[args.offset:args.offset + args.words * 4]))
    if 0xFFFFFFFF in words:
        words = words[:words.index(0xFFFFFFFF)]
    parts = [entry for entry in decode_records(words) if entry[0] == "part"]
    if not parts:
        raise SystemExit("no part records decoded")

    blob = bytearray()
    views: list[dict[str, int]] = []
    accessors: list[dict[str, object]] = []
    meshes: list[dict[str, object]] = []
    nodes: list[dict[str, object]] = []
    mesh_by_oba: dict[int, int] = {}

    def add_blob(data: bytes, target: int | None = None) -> int:
        offset = len(blob)
        blob.extend(data)
        view: dict[str, int] = {"buffer": 0, "byteOffset": offset,
                                "byteLength": len(data)}
        if target is not None:
            view["target"] = target
        views.append(view)
        return len(views) - 1

    for slot, (_, tpa, tha, oba) in enumerate(parts):
        if oba not in mesh_by_oba:
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
                {"bufferView": position_view, "componentType": 5126,
                 "count": len(vertices), "type": "VEC3",
                 "min": minimum, "max": maximum},
                {"bufferView": index_view, "componentType": 5125,
                 "count": len(indices), "type": "SCALAR"},
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
        translation = [slot * args.spread, 0.0, 0.0] if args.pose == "distribute" \
            else [0.0, 0.0, 0.0]
        nodes.append({
            "mesh": mesh_by_oba[oba],
            "name": f"slot_{slot:03d}_oba_{oba:08x}",
            "translation": translation,
            "rotation": [0.0, 0.0, 0.0, 1.0],
            "scale": [1.0, 1.0, 1.0],
            "extras": {"static_table": {"tpa": f"{tpa:08x}", "tha": f"{tha:08x}",
                                        "oba": f"{oba:08x}", "pose": args.pose}},
        })

    document = {
        "asset": {"version": "2.0", "generator": "von extract_static_frame.py"},
        "scene": 0,
        "scenes": [{"name": f"static_table_{args.offset:#x}", "nodes": list(range(len(nodes)))}],
        "nodes": nodes,
        "meshes": meshes,
        "buffers": [{"byteLength": len(blob), "uri": "data:application/octet-stream;base64," +
                     base64.b64encode(blob).decode("ascii")}],
        "bufferViews": views,
        "accessors": accessors,
        "extras": {"table_offset": f"{args.offset:#x}", "parts": len(parts),
                   "unique_meshes": len(meshes), "pose": args.pose},
    }
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n")
    print(f"wrote {len(parts)} static parts, {len(meshes)} unique meshes "
          f"to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
