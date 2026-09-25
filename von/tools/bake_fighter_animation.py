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
import statistics
from collections import defaultdict
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT
from bake_family_animation import (mat_inv3x4, mat_mul3x4, orthonormalize,
                                   quat_from_mat, row_major)

IDENT = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
PIVOT_LIMIT = 60.0


def load_parts(args):
    """Return [(key, oba), ...] where key is tpa (--match tpa) or oba.

    Duplicate keys (a shared skeleton part listed twice) collapse to one entry;
    the model has a single node per OBA, so duplicates would fight over it.
    """
    if args.obas:
        pairs = [(int(x, 16), int(x, 16)) for x in args.obas.replace(",", " ").split()]
    elif args.parts:
        d = json.loads(Path(args.parts).read_text())
        if args.match == "tpa":
            pairs = [(p["tpa"], p["oba"]) for p in d]
        else:
            pairs = [(p["oba"], p["oba"]) for p in d]
    else:
        raise SystemExit("provide --parts <Fighter.parts.json> or --obas")
    seen = set()
    out = []
    for key, oba in pairs:
        if key in seen:
            continue
        seen.add(key)
        out.append((key, oba))
    return out


def load_frame_tables(trace: Path, match: str):
    cur = IDENT
    frames = {}
    with trace.open(errors="replace") as fh:
        for line in fh:
            if "vonj_geometry_matrix" not in line and "vonj_geometry_object" not in line:
                continue
            m = MATRIX.search(line)
            if m:
                cur = row_major(m[2].split(","), m[3].split(","))
                continue
            m = OBJECT.search(line)
            if m and int(m[6]) == 3 and m[7] == "polygon-rom":
                key = int(m.group(2), 16) if match == "tpa" else int(m[4], 16)
                frames.setdefault(round(float(m[1]) * 60.0), {})[key] = cur
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
    """Single rooted skeleton: original stable edges + guaranteed connectivity.

    Keeps the historical candidate/rank selection (only pairs co-observed for
    many frames), which recovered good trees, then joins any leftover
    components and roots the result at the body core. The old version could
    leave a forest of parentless limbs pinned at the origin, anchoring the mech
    on whichever part escaped parenting (e.g. Viper II trailing its arm).
    """
    n = len(obas)
    min_samples = 10

    def mean_world(o):
        vals = [tb[o][9:12] for tb in tables if o in tb]
        if not vals:
            return None
        return [sum(v[k] for v in vals) / len(vals) for k in range(3)]

    means = [mean_world(o) for o in obas]
    core = [0.0, 0.0, 0.0]
    count = 0
    for tb in tables:
        pts = [tb[o][9:12] for o in obas if o in tb]
        if len(pts) < 3:
            continue
        for p in pts:
            for k in range(3):
                core[k] += p[k]
        count += len(pts)
    if count:
        core = [core[k] / count for k in range(3)]
    root = 0
    best = None
    for i, m in enumerate(means):
        if m is None:
            continue
        d = sum((m[k] - core[k]) ** 2 for k in range(3))
        if best is None or d < best:
            best = d
            root = i

    # Edge weight = joint rigidity (RMS of the parent-relative translation) plus
    # a bind-proximity term. Rigidity alone can prefer a far rigid part (a
    # weapon welded to a hand) and mis-parent skinned limbs; penalising the
    # bind distance keeps adjacent bones together, which recovers arm/leg
    # chains even when a fighter's capture only contains some of its parts.
    bind_weight = 1.0

    def pair_weight(ci, pi):
        vals = []
        for tb in tables:
            if obas[ci] in tb and obas[pi] in tb:
                local = mat_mul3x4(mat_inv3x4(tb[obas[pi]]), tb[obas[ci]])
                vals.append(local[9:12])
        md = 0.0
        if means[ci] is not None and means[pi] is not None:
            md = math.sqrt(sum((means[ci][k] - means[pi][k]) ** 2 for k in range(3)))
        if len(vals) >= 2:
            mean = [sum(v[k] for v in vals) / len(vals) for k in range(3)]
            rms = math.sqrt(sum(sum((v[k] - mean[k]) ** 2 for k in range(3))
                                 for v in vals) / len(vals))
            return rms + bind_weight * md, len(vals)
        if means[ci] is not None and means[pi] is not None:
            return md * (1.0 + bind_weight), 0
        return 1e9, 0

    # Main tree edges: original candidate/rank selection.
    cand = [[] for _ in range(n)]
    for ci in range(n):
        for pi in range(n):
            if ci == pi:
                continue
            rms, samples = pair_weight(ci, pi)
            if samples >= min_samples:
                cand[ci].append((rms, pi))
        cand[ci].sort()
    edges = []
    for ci in range(n):
        for rank, (rms, pi) in enumerate(cand[ci][:4]):
            edges.append((rms + rank * 100.0, ci, pi))
    edges.sort()

    uf = list(range(n))

    def find(x):
        while uf[x] != x:
            uf[x] = uf[uf[x]]
            x = uf[x]
        return x

    adj = [[] for _ in range(n)]
    parent = [-1] * n
    for _, ci, pi in edges:
        if parent[ci] != -1:
            continue
        if find(ci) == find(pi):
            continue
        parent[ci] = pi
        uf[find(ci)] = find(pi)
        adj[ci].append(pi)
        adj[pi].append(ci)

    # Connectivity: attach leftover components with the cheapest available edge.
    allpairs = []
    for ci in range(n):
        for pi in range(ci + 1, n):
            rms, samples = pair_weight(ci, pi)
            allpairs.append((rms + (0.0 if samples >= min_samples else 1000.0),
                             ci, pi))
    allpairs.sort()
    while len({find(i) for i in range(n)}) > 1:
        pick = None
        for _, ci, pi in allpairs:
            if find(ci) != find(pi):
                pick = (ci, pi)
                break
        if pick is None:
            break
        ci, pi = pick
        uf[find(ci)] = find(pi)
        adj[ci].append(pi)
        adj[pi].append(ci)

    parent = [-2] * n
    parent[root] = -1
    stack = [root]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if parent[v] == -2:
                parent[v] = u
                stack.append(v)
    for i in range(n):
        if parent[i] == -2:
            parent[i] = root
    return parent, root


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--fighter", required=True)
    ap.add_argument("--parts", type=Path)
    ap.add_argument("--obas")
    ap.add_argument("--match", choices=("oba", "tpa"), default="oba")
    ap.add_argument("--clip", default="clip")
    ap.add_argument("--t0", type=float, default=0.0)
    ap.add_argument("--t1", type=float, default=1e9)
    ap.add_argument("--min-parts", type=int, default=4)
    ap.add_argument("--tree", type=Path,
                    help="optional skeleton override JSON {root, parents:{child:parent}}")
    ap.add_argument("--observed-only", action="store_true",
                    help="drop parts the capture never emits and parent each kept "
                         "part through its nearest observed ancestor, so a limb "
                         "whose parent is only present in other captures does not "
                         "collapse onto the torso")
    args = ap.parse_args()

    parts_list = load_parts(args)
    keys_list = [k for k, _ in parts_list]
    obas_out = [o for _, o in parts_list]
    n = len(keys_list)
    print(f"fighter {args.fighter}: {n} parts (match={args.match})")
    frames = load_frame_tables(args.trace, args.match)
    want = set(keys_list)
    keys = sorted(k for k, tb in frames.items()
                  if len(want & set(tb)) >= args.min_parts and args.t0 <= k / 60.0 <= args.t1)
    run, s, e = longest_run(keys)
    keys = keys[s:e]
    if len(keys) < 2:
        raise SystemExit(f"only {len(keys)} frames")
    print(f"frames: {len(keys)}  t={keys[0]/60:.2f}..{keys[-1]/60:.2f}")

    if args.tree:
        override = json.loads(args.tree.read_text())
        index_of = {f"{obas_out[i]:08x}": i for i in range(n)}
        root = index_of.get(str(override["root"]).lower().replace("0x", ""), 0)
        parent = [-1] * n
        for child, par in override.get("parents", {}).items():
            ci = index_of.get(str(child).lower().replace("0x", ""))
            pi = index_of.get(str(par).lower().replace("0x", ""))
            if ci is not None and pi is not None:
                parent[ci] = pi
    else:
        parent, root = infer_tree([frames[k] for k in keys], keys_list)
    print(f"root: {keys_list[root]:08x}")
    for i in range(n):
        print(f"  {keys_list[i]:08x} <- {keys_list[parent[i]]:08x}" if parent[i] >= 0
              else f"  {keys_list[i]:08x} (root)")

    # Which parts this capture actually emits (observed). With --observed-only,
    # any part never seen is dropped and each kept part is parented through its
    # nearest observed ancestor, so a limb whose immediate parent lives only in
    # another capture is still baked from the same relative transform the
    # runtime will compose (otherwise it collapses onto the torso).
    present_counts = [sum(1 for k in keys if obas_out[i] in frames[k])
                      for i in range(n)]
    if args.observed_only:
        observed = [c >= 2 for c in present_counts]

        def effective_parent(i):
            p = parent[i]
            while p >= 0 and not observed[p]:
                p = parent[p]
            return p

        eff = [effective_parent(i) for i in range(n)]
        kept = [i for i in range(n) if observed[i]]
        remap = {i: j for j, i in enumerate(kept)}
        out_parent = [remap[eff[i]] if eff[i] >= 0 else -1 for i in kept]
        out_root = remap.get(root)
        if out_root is None:
            out_root = 0
        n = len(kept)
    else:
        kept = list(range(n))
        remap = {i: i for i in range(n)}
        out_parent = list(parent)
        out_root = root

    last = [IDENT] * n
    measured = [0] * n
    quats = [[] for _ in range(n)]
    trans = [[] for _ in range(n)]
    samples = [[] for _ in range(n)]
    for k in keys:
        tb = frames[k]
        for j, i in enumerate(kept):
            oba = keys_list[i]
            p_out = out_parent[j]
            p = kept[p_out] if p_out >= 0 else -1
            if p < 0:
                local = IDENT
            elif oba in tb and keys_list[p] in tb:
                local = mat_mul3x4(mat_inv3x4(tb[keys_list[p]]), tb[oba])
                last[j] = local
            else:
                local = last[j]
            if oba in tb:
                measured[j] += 1
                samples[j].append(local[9:12])
            # The ROM animates each part's translation as well as its rotation,
            # so keep the per-frame translation; averaging it to one pivot
            # (the old behavior) made telescoping limbs drift.
            trans[j].append(local[9:12])
            quats[j].append(quat_from_mat(orthonormalize(local[:9])))
    # Median pivot (robust to a shared part momentarily matching the other
    # fighter) with an absolute clamp so a corrupt joint cannot fling a limb.
    pivots = []
    for j in range(n):
        if not samples[j]:
            pivots.append([0.0, 0.0, 0.0])
            continue
        cols = list(zip(*samples[j]))
        piv = [statistics.median(c) for c in cols]
        if math.sqrt(sum(v * v for v in piv)) > PIVOT_LIMIT:
            piv = [0.0, 0.0, 0.0]
        pivots.append(piv)
    print("parts present:", sum(1 for m in measured if m > 0), "/", n)

    out = {
        "schema": "von-animation-bake/1",
        "fighter": args.fighter,
        "clip": args.clip,
        "fps": 60.0,
        "frame_count": len(keys),
        "root": out_root,
        "parts": [{"oba": f"{obas_out[kept[j]]:08x}", "parent": out_parent[j],
                   "pivot": [round(v, 5) for v in pivots[j]]}
                  for j in range(n)],
        "quats": [[[round(v, 5) for v in quats[j][f]] for j in range(n)]
                  for f in range(len(keys))],
        "trans": [[[round(v, 5) for v in trans[j][f]] for j in range(n)]
                  for f in range(len(keys))],
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")
    print(f"wrote {args.out} ({args.out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
