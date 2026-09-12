#!/usr/bin/env python3
"""Bake a per-fighter rig + clip for any fighter present in a geometry capture.

Unlike `bake_family_animation.py` (Temjin tree hardcoded), this loads the
fighter's OBA set from its ROM part table (`<Fighter>.parts.json`) and infers
the parent tree from the capture by minimizing the variance of the
parent-relative translation `inv(W_parent) * W_child`, then bakes the FK model

    world(child) = world(parent) * Translate(pivot) * R(frame)

with carry-forward for culled parts and longest-contiguous-run selection.
"""
from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT
from bake_family_animation import mat_inv3x4, mat_mul3x4, orthonormalize, quat_from_mat

IDENT = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)


def load_obas(args) -> list[int]:
    if args.obas:
        return [int(x, 16) for x in args.obas.replace(",", " ").split()]
    if args.parts:
        d = json.loads(Path(args.parts).read_text())
        return [p["oba"] for p in d]
    raise SystemExit("provide --parts <Fighter.parts.json> or --obas")


def load_frame_tables(trace: Path):
    cur = IDENT
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
                frames.setdefault(round(float(m[1]) * 60.0), {})[int(m[4], 16)] = cur
    return frames


def longest_run(keys):
    best = (0, 0, 0)
    start = 0
    for i in range(1, len(keys) + 1):
        if i == len(keys) or keys[i] - keys[i - 1] > 2:
            if i - start > best[0]:
                best = (i - start, start, i)
            start = i
    return best


def infer_tree(tables, obas):
    """Kruskal-style parent inference: cheapest parent-relative-translation
    edges that keep the graph acyclic."""
    n = len(obas)
    cand = [list() for _ in range(n)]
    meas = [0] * n
    for ci, co in enumerate(obas):
        for pi, po in enumerate(obas):
            if pi == ci:
                continue
            vals = []
            for tb in tables:
                if co in tb and po in tb:
                    local = mat_mul3x4(mat_inv3x4(tb[po]), tb[co])
                    vals.append(local[9:12])
            if len(vals) < 10:
                continue
            meas[ci] += len(vals)
            mean = [sum(v[k] for v in vals) / len(vals) for k in range(3)]
            rms = math.sqrt(sum(sum((v[k] - mean[k]) ** 2 for k in range(3))
                                 for v in vals) / len(vals))
            cand[ci].append((rms, pi))
        cand[ci].sort()
    parent = [-1] * n
    uf = list(range(n))

    def find(x):
        while uf[x] != x:
            uf[x] = uf[uf[x]]
            x = uf[x]
        return x

    edges = []
    for ci in range(n):
        for rank, (rms, pi) in enumerate(cand[ci][:4]):
            edges.append((rms + rank * 100.0, ci, pi))
    edges.sort()
    used = 0
    for _, ci, pi in edges:
        if parent[ci] != -1:
            continue
        if find(ci) == find(pi):
            continue
        parent[ci] = pi
        uf[find(ci)] = find(pi)
        used += 1
        if used == n - 1:
            break
    root = next((i for i in range(n) if parent[i] == -1), 0)
    return parent, root


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fighter", required=True)
    ap.add_argument("--parts", type=Path)
    ap.add_argument("--obas")
    ap.add_argument("--clip", default="clip")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=1e9)
    ap.add_argument("--min-parts", type=int, default=4)
    args = ap.parse_args()

    obas = load_obas(args)
    n = len(obas)
    print(f"fighter {args.fighter}: {n} parts")
    frames = load_frame_tables(args.trace)
    want = set(obas)
    keys = sorted(k for k, tb in frames.items()
                  if len(want & set(tb)) >= args.min_parts)
    run, s, e = longest_run(keys)
    keys = [k for k in keys[s:e] if args.t0 <= k / 60.0 <= args.t1]
    if len(keys) < 2:
        raise SystemExit(f"only {len(keys)} frames")
    print(f"frames: {len(keys)}  t={keys[0]/60:.2f}..{keys[-1]/60:.2f}")

    parent, root = infer_tree([frames[k] for k in keys], obas)
    print(f"root: {obas[root]:08x}")
    for i in range(n):
        print(f"  {obas[i]:08x} <- {obas[parent[i]]:08x}" if parent[i] >= 0
              else f"  {obas[i]:08x} (root)")

    last = [IDENT] * n
    tsum = [[0.0, 0.0, 0.0] for _ in range(n)]
    measured = [0] * n
    quats = [[] for _ in range(n)]
    for k in keys:
        tb = frames[k]
        for i, oba in enumerate(obas):
            p = parent[i]
            if p < 0:
                local = IDENT
            elif oba in tb and obas[p] in tb:
                local = mat_mul3x4(mat_inv3x4(tb[obas[p]]), tb[oba])
                last[i] = local
            else:
                local = last[i]
            if oba in tb:
                measured[i] += 1
                for c in range(3):
                    tsum[i][c] += local[9 + c]
            quats[i].append(quat_from_mat(orthonormalize(local[:9])))
    pivots = [[tsum[i][c] / measured[i] if measured[i] else 0.0 for c in range(3)]
              for i in range(n)]
    print("parts present:", sum(1 for m in measured if m > 0), "/", n)

    out = {
        "fighter": args.fighter,
        "clip": args.clip,
        "fps": 60.0,
        "frame_count": len(keys),
        "root": root,
        "parts": [{"oba": f"{o:08x}", "parent": parent[i],
                   "pivot": [round(v, 5) for v in pivots[i]]}
                  for i, o in enumerate(obas)],
        "quats": [[[round(v, 5) for v in quats[i][f]] for i in range(n)]
                  for f in range(len(keys))],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
