#!/usr/bin/env python3
"""Bake a per-fighter rig + clip from a geometry capture.

For a known fighter family (canonical OBA order + parent tree), this reads the
world matrices from a `vonj_geometry_matrix` trace, computes each part's
parent-relative local transform `inv(W_parent) * W_child`, decomposes it into a
(translation, rotation-quaternion), and writes a compact clip JSON.

The FK model is the recovered one

    world(child) = world(parent) * Translate(pivot) * R(frame)

so the clip stores a constant pivot per joint plus a per-frame rotation. The
kernel plays the quaternion series and does the FK.

Temjin's canonical slots/OBAs and tree come from
von-runner/docs/temjin-rig-analysis.md.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT

# Temjin family-08: slot -> OBA (slots 006..024).
TEMJIN_SLOTS = [
    "009e410d", "009e3f80", "009e43a8", "009e3c34", "009e3aa7", "009e3ecf",
    "009e2a84", "009e35b7", "009e2ea2", "009e30ab", "009e343a", "009e3588",
    "008964ba", "009e2f5d", "009e3300", "008ad656", "009e332f", "009e2cb1",
    "009e36c2",
]
# child index -> parent index (0-based, from temjin-rig-analysis.md slot maps).
TEMJIN_TREE = {
    0: 1, 1: 4, 4: 5, 5: 6, 6: 17, 17: 18, 18: 16,
    3: 4, 2: 6, 7: 11, 11: 12, 12: 2, 8: 17, 10: 11,
    14: 16, 13: 14, 15: 13, 9: 15,
}
TEMJIN_ROOT = 16  # slot 022 = 009e332f


def mat_inv3x4(m):
    r = m[:9]
    d = (r[0] * (r[4] * r[8] - r[5] * r[7]) - r[1] * (r[3] * r[8] - r[5] * r[6])
         + r[2] * (r[3] * r[7] - r[4] * r[6]))
    if abs(d) < 1e-12:
        return None
    inv = ((r[4] * r[8] - r[5] * r[7]) / d, (r[2] * r[7] - r[1] * r[8]) / d,
           (r[1] * r[5] - r[2] * r[4]) / d, (r[5] * r[6] - r[3] * r[8]) / d,
           (r[0] * r[8] - r[2] * r[6]) / d, (r[2] * r[3] - r[0] * r[5]) / d,
           (r[3] * r[7] - r[4] * r[6]) / d, (r[1] * r[6] - r[0] * r[7]) / d,
           (r[0] * r[4] - r[1] * r[3]) / d)
    t = m[9:12]
    nt = tuple(-sum(inv[row * 3 + c] * t[c] for c in range(3)) for row in range(3))
    return inv + nt


def mat_mul3x4(a, b):
    r = tuple(sum(a[row * 3 + k] * b[k * 3 + c] for k in range(3))
              for row in range(3) for c in range(3))
    t = tuple(a[9 + row] + sum(a[row * 3 + k] * b[9 + k] for k in range(3))
              for row in range(3))
    return r + t


def orthonormalize(r):
    # Gram-Schmidt on columns; the trace matrices carry scale.
    c0 = [r[0], r[3], r[6]]
    c1 = [r[1], r[4], r[7]]
    def norm(v):
        n = math.sqrt(sum(x * x for x in v))
        return [x / n for x in v] if n > 1e-9 else [0.0, 0.0, 0.0]
    e0 = norm(c0)
    d = sum(e0[i] * c1[i] for i in range(3))
    c1 = [c1[i] - d * e0[i] for i in range(3)]
    e1 = norm(c1)
    e2 = [e0[1] * e1[2] - e0[2] * e1[1], e0[2] * e1[0] - e0[0] * e1[2],
          e0[0] * e1[1] - e0[1] * e1[0]]
    return (e0[0], e1[0], e2[0], e0[1], e1[1], e2[1], e0[2], e1[2], e2[2])


def quat_from_mat(r):
    tr = r[0] + r[4] + r[8]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        w = 0.25 * s
        x = (r[7] - r[5]) / s
        y = (r[2] - r[6]) / s
        z = (r[3] - r[1]) / s
    elif r[0] > r[4] and r[0] > r[8]:
        s = math.sqrt(1.0 + r[0] - r[4] - r[8]) * 2
        w = (r[7] - r[5]) / s
        x = 0.25 * s
        y = (r[1] + r[3]) / s
        z = (r[2] + r[6]) / s
    elif r[4] > r[8]:
        s = math.sqrt(1.0 + r[4] - r[0] - r[8]) * 2
        w = (r[2] - r[6]) / s
        x = (r[1] + r[3]) / s
        y = 0.25 * s
        z = (r[5] + r[7]) / s
    else:
        s = math.sqrt(1.0 + r[8] - r[0] - r[4]) * 2
        w = (r[3] - r[1]) / s
        x = (r[2] + r[6]) / s
        y = (r[5] + r[7]) / s
        z = 0.25 * s
    return [x, y, z, w]


def load_frames(trace: Path, obas: list[int], start: int):
    """Collect frames where every canonical OBA is present (any submission order)."""
    cur = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
    frames = {}
    with trace.open(errors="replace") as fh:
        for line in fh:
            if "vonj_geometry_matrix" not in line and "vonj_geometry_object" not in line:
                continue
            m = MATRIX.search(line)
            if m:
                cur = (tuple(float(x) for x in m[2].split(","))
                       + tuple(float(x) for x in m[3].split(",")))
                continue
            m = OBJECT.search(line)
            if m and int(m[6]) == 3 and m[7] == "polygon-rom":
                # Group objects into 60 Hz frames; per-object timestamps differ
                # by microseconds within one rendered frame.
                frames.setdefault(round(float(m[1]) * 60.0), {})[int(m[4], 16)] = cur
    want = set(obas)
    selected = []
    for t, table in sorted(frames.items()):
        if want <= set(table):
            selected.append((t / 60.0, [table[o] for o in obas]))
    # Keep the longest contiguous run (gaps <= 2 frames) for smooth playback.
    if selected:
        idx = [int(round(t * 60.0)) for t, _ in selected]
        best = (0, 0, 0)
        start = 0
        for i in range(1, len(idx) + 1):
            if i == len(idx) or idx[i] - idx[i - 1] > 2:
                run = i - start
                if run > best[0]:
                    best = (run, start, i)
                start = i
        selected = selected[best[1]:best[2]]
    return selected


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--fighter", default="temjin")
    ap.add_argument("--clip", default="walk")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=1e9)
    args = ap.parse_args()

    obas = [int(x, 16) for x in TEMJIN_SLOTS]
    selected = [(t, w) for t, w in load_frames(args.trace, obas, 6)
                if args.t0 <= t <= args.t1]
    if len(selected) < 2:
        raise SystemExit(f"only {len(selected)} exact Temjin frames in window")
    print(f"frames: {len(selected)}  t={selected[0][0]:.3f}..{selected[-1][0]:.3f}")

    n = len(obas)
    root = TEMJIN_ROOT
    # per-frame local (pivot translation + rotation) for every part
    pivots = [None] * n
    trans_sum = [[0.0, 0.0, 0.0] for _ in range(n)]
    quats = [[] for _ in range(n)]
    for _, world in selected:
        for i in range(n):
            parent = TEMJIN_TREE.get(i)
            if i == root or parent is None:
                local = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
            else:
                inv_p = mat_inv3x4(world[parent])
                local = mat_mul3x4(inv_p, world[i])
            for k in range(3):
                trans_sum[i][k] += local[9 + k]
            quats[i].append(quat_from_mat(orthonormalize(local[:9])))
    for i in range(n):
        pivots[i] = [trans_sum[i][k] / len(selected) for k in range(3)]

    out = {
        "fighter": args.fighter,
        "clip": args.clip,
        "fps": 60.0,
        "frame_count": len(selected),
        "root": root,
        "parts": [{"oba": f"{o:08x}", "parent": TEMJIN_TREE.get(i, -1),
                   "pivot": [round(v, 5) for v in pivots[i]]}
                  for i, o in enumerate(obas)],
        "quats": [[[round(v, 5) for v in quats[i][f]] for i in range(n)]
                  for f in range(len(selected))],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
