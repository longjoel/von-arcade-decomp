#!/usr/bin/env python3
"""Fit a parametric hinge-joint model from family world-matrix frames.

For each parent->child edge of a hypothesized rig tree, computes the
parent-relative local transform L(t) = inverse(P(t)) * C(t) across all
exact-canonical family frames and tests the hinge hypothesis:

  * local translation is constant (pivot fixed in the parent frame),
  * local rotation varies about ONE fixed axis (single hinge angle),
  * local scale is ~1 (rigid part).

A joint that passes is parametric: its full motion is one scalar angle
series theta(t) plus constant (pivot, axis) vectors. Output JSON holds
the fitted constants and per-frame angle series for animation use.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT


# Temjin family-08 hypothesis from von-runner/docs/temjin-rig-analysis.md:
# slots 006..024 map to canonical indices 0..18; child slot -> parent slot.
TREE_SLOTS = {
    6: 7, 7: 10, 10: 11, 11: 12, 12: 23, 23: 24, 24: 22,
    9: 10, 8: 12, 13: 17, 17: 18, 18: 8, 14: 23, 16: 17,
    20: 22, 19: 20, 21: 19, 15: 21,
}
ROOT_SLOT = 22


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
    t = tuple(sum(a[row * 3 + k] * b[9 + k] for k in range(3)) + a[9 + row]
              for row in range(3))
    return r + t


def axis_angle(r):
    """Rotation axis (unit) and angle of a 3x3 rotation matrix."""
    x = (r[7] - r[5]) / 2.0
    y = (r[2] - r[6]) / 2.0
    z = (r[3] - r[1]) / 2.0
    s = math.sqrt(x * x + y * y + z * z)
    c = max(-1.0, min(1.0, (r[0] + r[4] + r[8] - 1.0) / 2.0))
    if s < 1e-9:
        return (1.0, 0.0, 0.0), 0.0
    return (x / s, y / s, z / s), math.atan2(s, c)


def load_frames(trace: Path, obas: list[int], start: int):
    cur = (1., 0., 0., 0., 1., 0., 0., 0., 1., 0., 0., 0.)
    frames: dict[float, list] = {}
    with trace.open(errors="replace") as fh:
        for line in fh:
            line = line.rstrip()
            m = MATRIX.search(line)
            if m:
                cur = (tuple(float(x) for x in m[2].split(","))
                       + tuple(float(x) for x in m[3].split(",")))
                continue
            m = OBJECT.search(line)
            if m and int(m[6]) == 3 and m[7] == "polygon-rom":
                frames.setdefault(float(m[1]), []).append((int(m[4], 16), cur))
    n = len(obas)
    selected = []
    for _, objs in sorted(frames.items()):
        window = objs[start:start + n]
        if len(window) == n and [v[0] for v in window] == obas:
            selected.append([v[1] for v in window])
    return selected


def fit_edge(pi: int, ci: int, frames):
    """Fit one joint. Returns dict with hinge statistics and angle series."""
    n = len(frames)
    trans = []
    scales = []
    rots = []
    for f in frames:
        pinv = mat_inv3x4(f[pi])
        if pinv is None:
            continue
        loc = mat_mul3x4(pinv, f[ci])
        trans.append(loc[9:12])
        r = loc[:9]
        scales.append(tuple(math.sqrt(r[c] ** 2 + r[3 + c] ** 2 + r[6 + c] ** 2)
                            for c in range(3)))
        rots.append(r)
    m = len(rots)
    mean_t = [sum(t[i] for t in trans) / m for i in range(3)]
    trans_rms = math.sqrt(sum(
        sum((t[i] - mean_t[i]) ** 2 for i in range(3)) for t in trans) / m)
    mean_s = [sum(s[i] for s in scales) / m for i in range(3)]
    # Rotation excursion relative to first frame: D(t) = R(t) * R(0)^T.
    r0t = (rots[0][0], rots[0][3], rots[0][6],
           rots[0][1], rots[0][4], rots[0][7],
           rots[0][2], rots[0][5], rots[0][8])
    axes = []
    angles = []
    for r in rots:
        d = tuple(sum(r[row * 3 + k] * r0t[k * 3 + c] for k in range(3))
                  for row in range(3) for c in range(3))
        a, th = axis_angle(d)
        # Unwrap axis sign against running mean for stability measurement.
        if axes and sum(a[i] * axes[-1][i] for i in range(3)) < 0:
            a = (-a[0], -a[1], -a[2])
            th = -th
        axes.append(a)
        angles.append(th)
    # Mean axis weighted by excursion size (near-identity frames carry no axis).
    wsum = [0.0, 0.0, 0.0]
    wtot = 0.0
    for a, th in zip(axes, angles):
        w = abs(math.sin(th))
        wtot += w
        for i in range(3):
            wsum[i] += w * a[i]
    if wtot > 1e-9:
        wl = math.sqrt(sum(v * v for v in wsum))
        mean_axis = tuple(v / wl for v in wsum)
    else:
        mean_axis = (0.0, 0.0, 0.0)  # joint never rotates
    spread = 0.0
    for a, th in zip(axes, angles):
        if abs(math.sin(th)) < 0.05:
            continue
        cosang = max(-1.0, min(1.0, sum(a[i] * mean_axis[i] for i in range(3))))
        spread = max(spread, math.degrees(math.acos(cosang)))
    return {
        "parent_index": pi,
        "child_index": ci,
        "frames": m,
        "pivot_parent_frame": [round(v, 4) for v in mean_t],
        "translation_rms": round(trans_rms, 5),
        "mean_scale": [round(v, 5) for v in mean_s],
        "hinge_axis_parent_frame": [round(v, 5) for v in mean_axis],
        "axis_spread_deg": round(spread, 3),
        "angle_min_deg": round(math.degrees(min(angles)), 3),
        "angle_max_deg": round(math.degrees(max(angles)), 3),
        "angle_series_deg": [round(math.degrees(a), 4) for a in angles],
        "hinge": bool(trans_rms < 2.0 and (wtot <= 1e-9 or spread < 5.0)),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fingerprints", type=Path, required=True)
    p.add_argument("--family", required=True)
    p.add_argument("--trace", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    d = json.loads(a.fingerprints.read_text())
    fam = next(x for x in d["families"] if x["family"] == a.family)
    obas = [int(x, 16) for x in fam["canonical_obas"]]
    start = fam["first_slot"]
    frames = load_frames(a.trace, obas, start)
    print(f"exact canonical frames: {len(frames)}")
    if len(frames) < 2:
        raise SystemExit("fewer than two exact family frames")
    edges = {c - start: p_ - start for c, p_ in TREE_SLOTS.items()
             if start <= c < start + len(obas) and start <= p_ < start + len(obas)}
    joints = []
    for ci, pi in sorted(edges.items()):
        j = fit_edge(pi, ci, frames)
        j["parent_slot"] = start + pi
        j["child_slot"] = start + ci
        j["parent_oba"] = f"{obas[pi]:08x}"
        j["child_oba"] = f"{obas[ci]:08x}"
        joints.append(j)
        print(f"child {j['child_slot']:03d} <- parent {j['parent_slot']:03d} "
              f"n={j['frames']} trans_rms={j['translation_rms']:.4f} "
              f"axis_spread={j['axis_spread_deg']:.2f}deg "
              f"theta=[{j['angle_min_deg']:.1f},{j['angle_max_deg']:.1f}] "
              f"scale={[f'{v:.3f}' for v in j['mean_scale']]} "
              f"{'HINGE' if j['hinge'] else 'complex'}")
    out = {"family": a.family, "root_slot": ROOT_SLOT,
           "frames": len(frames), "joints": joints}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {a.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
