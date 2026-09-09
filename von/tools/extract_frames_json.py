#!/usr/bin/env python3
"""Extract a frames JSON tap from a patched-MAME geometry trace.

Reads vonj_geometry_matrix / vonj_geometry_object events from a mame.log,
pairs each object with its most recent matrix (same rule as
annotate_bout.load_frames), keeps mode-3 polygon-rom objects, and emits
the frames format {t: [[oba, tpa, tha, r0..r8, x, y, z], ...]} with
integer tpa/tha (entry_meta-compatible).

Usage: extract_frames_json.py --trace mame.log --output frames.json
    [--t0 138 --t1 172]
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trace", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--t0", type=float, default=None)
    p.add_argument("--t1", type=float, default=None)
    a = p.parse_args()
    frames: dict[str, list] = {}
    cur = None
    n_obj = n_keep = 0
    with a.trace.open(errors="replace") as fh:
        for raw in fh:
            line = raw.rstrip()
            m = MATRIX.search(line)
            if m:
                cur = (tuple(float(x) for x in m.group(2).split(","))
                       + tuple(float(x) for x in m.group(3).split(",")))
                continue
            m = OBJECT.search(line)
            if m and int(m.group(6)) == 3 and m.group(7) == "polygon-rom":
                n_obj += 1
                t = float(m.group(1))
                if ((a.t0 is None or t >= a.t0)
                        and (a.t1 is None or t <= a.t1) and cur is not None):
                    n_keep += 1
                    frames.setdefault(f"{t:.6f}", []).append(
                        [m.group(4), int(m.group(2), 16), int(m.group(3), 16),
                         *cur])
    a.output.write_text(json.dumps(frames) + "\n")
    print(f"frames: {len(frames)} kept {n_keep}/{n_obj} polygon-rom objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
