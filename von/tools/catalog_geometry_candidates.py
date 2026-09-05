#!/usr/bin/env python3
"""List spatially separated, fingerprinted geometry candidates for one trace frame."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from export_geometry_assemblies import split_assemblies
from export_geometry_frame_textured_gltf import select_frame


def path_error(label: str, path: Path, root: Path, *, output: bool = False) -> str | None:
    if path.is_symlink():
        return f"{label} path must not be a symlink: {path}"
    try:
        path.resolve().relative_to(root.resolve())
    except (OSError, RuntimeError, ValueError):
        return f"{label} path escapes root: {path}"
    if not output and not path.is_file():
        return f"missing {label}: {path}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--time", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="root that geometry trace and candidate output must remain within")
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=.02)
    parser.add_argument("--distance", type=float, default=15.0)
    args = parser.parse_args()
    root = args.root.resolve()
    for label, path, output in (("trace", args.trace, False), ("output", args.output, True)):
        error = path_error(label, path, root, output=output)
        if error:
            print(f"Geometry candidates: {error}")
            return 1
    if args.distance <= 0:
        raise SystemExit("distance must be positive")
    selected_time, objects = select_frame(args.trace, args.time, None, args.tolerance, args.min_objects)
    groups = split_assemblies(objects, args.distance)
    candidates = []
    for group in groups:
        start = group[0][0]
        entries = [entry for _, entry in group]
        signature = [int(entry[0]) for entry in entries]
        digest = hashlib.sha256(b"".join(value.to_bytes(4, "little") for value in signature)).hexdigest()[:16]
        candidates.append({"candidate": f"oba-{digest}", "start_slot": start, "object_count": len(group),
                           "obas": [f"{value:08x}" for value in signature],
                           "mode": sorted(set(int(entry[2]["mode"]) for entry in entries)),
                           "source": sorted(set(str(entry[2]["source"]) for entry in entries)),
                           "status": "candidate"})
    result = {"trace": str(args.trace), "trace_time": selected_time, "frame_objects": len(objects), "candidates": candidates}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"cataloged {len(candidates)} spatial candidates from {len(objects)} objects")
    return 0
if __name__ == "__main__":
    raise SystemExit(main())
