#!/usr/bin/env python3
"""Partition one traced frame into spatial assemblies and export static ROM glTFs."""
from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path

from export_geometry_triangle_build_gltf import select_geometry


def split_assemblies(objects, distance: float):
    """Keep submission order; begin an assembly when adjacent origins separate."""
    groups = []
    for slot, item in enumerate(objects):
        origin = item[1][9:12]
        if not groups:
            groups.append([(slot, item)])
            continue
        prior = groups[-1][-1][1][1][9:12]
        if math.dist(origin, prior) > distance:
            groups.append([])
        groups[-1].append((slot, item))
    return groups


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--rom", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--time", type=float)
    parser.add_argument("--max-time", type=float)
    parser.add_argument("--tolerance", type=float, default=0.02)
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--distance", type=float, default=15.0,
                        help="world-space gap that begins the next assembly")
    args = parser.parse_args()
    if args.distance <= 0.0:
        raise SystemExit("--distance must be positive")
    selected_time, objects = select_geometry(args.trace, args.time, args.tolerance,
                                              args.min_objects, args.max_time)
    groups = split_assemblies(objects, args.distance)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    exporter = Path(__file__).with_name("export_geometry_frame_gltf.py")
    manifest = {"trace_time": selected_time, "distance": args.distance, "assemblies": []}
    for ordinal, group in enumerate(groups):
        start = group[0][0]
        output = args.output_dir / f"assembly-{ordinal:02d}-slot-{start:02d}.gltf"
        subprocess.run(["python3", exporter, "--trace", args.trace, "--rom", args.rom,
                        "--output", output, "--time", str(selected_time),
                        "--tolerance", str(args.tolerance), "--min-objects", str(args.min_objects),
                        "--start-object", str(start), "--max-objects", str(len(group))], check=True)
        manifest["assemblies"].append({"ordinal": ordinal, "start_slot": start,
            "object_count": len(group), "output": output.name,
            "obas": [f"{item[0]:08x}" for _, item in group]})
    (args.output_dir / "assemblies.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"wrote {len(groups)} ROM-backed assemblies at timestamp {selected_time:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
