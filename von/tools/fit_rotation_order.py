#!/usr/bin/env python3
"""Determine the firmware rotation-composition order per joint.

The SHARC rotation opcodes left-multiply affine state by single-axis
rotations (0x14=Rx, 0x15=Ry, 0x16=Rz). A joint's local rotation is
therefore R1(a)*R2(b)*R3(c) for some axis order. For each candidate
order, track the angle triple across frames (seeded local optimization
for continuity) and score total variation of the unwrapped series. The
firmware's true order yields smooth series; wrong orders gimbal-flip.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fit_parametric_rig import mat_inv3x4, mat_mul3x4, load_frames


def rot(axis: str, t: float) -> np.ndarray:
    c, s = math.cos(t), math.sin(t)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def forward(order, a):
    return rot(order[0], a[0]) @ rot(order[1], a[1]) @ rot(order[2], a[2])


def track(order, mats):
    """Seeded coordinate-descent angle tracking. Returns (angles, residual)."""
    ang = np.zeros(3)
    series = []
    resid = 0.0
    for m in mats:
        target = np.array(m[:9]).reshape(3, 3)
        # Normalize scale out (column norms ~1 anyway).
        target = target / np.linalg.norm(target, axis=0, keepdims=True)
        for _ in range(40):
            improved = False
            for k in range(3):
                for step in (0.02, 0.005, 0.001):
                    for sgn in (1.0, -1.0):
                        trial = ang.copy()
                        trial[k] += sgn * step
                        if (np.linalg.norm(forward(order, trial) - target)
                                < np.linalg.norm(forward(order, ang) - target)):
                            ang = trial
                            improved = True
            if not improved:
                break
        series.append(tuple(ang))
        resid += float(np.linalg.norm(forward(order, ang) - target))
    return series, resid / len(mats)


def total_variation(series):
    arr = np.unwrap(np.array(series), axis=0)
    return float(np.sum(np.abs(np.diff(arr, axis=0))))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fingerprints", type=Path, required=True)
    p.add_argument("--family", required=True)
    p.add_argument("--trace", type=Path, required=True)
    p.add_argument("--joints", default="13-14,15-13,10-11,12-2,11-12",
                   help="child-parent index pairs")
    a = p.parse_args()
    d = json.loads(a.fingerprints.read_text())
    fam = next(x for x in d["families"] if x["family"] == a.family)
    obas = [int(x, 16) for x in fam["canonical_obas"]]
    frames = load_frames(a.trace, obas, fam["first_slot"])
    print(f"frames: {len(frames)}")
    for spec in a.joints.split(","):
        ci, pi = (int(v) for v in spec.split("-"))
        mats = []
        for f in frames:
            inv = mat_inv3x4(f[pi])
            if inv is not None:
                mats.append(mat_mul3x4(inv, f[ci]))
        print(f"--- joint child={ci} parent={pi} n={len(mats)}")
        results = []
        for order in itertools.permutations("xyz"):
            series, resid = track(order, mats)
            tv = total_variation(series)
            results.append((tv, resid, order, series))
        results.sort()
        for tv, resid, order, series in results:
            arr = np.degrees(np.unwrap(np.array(series), axis=0))
            ranges = [(round(float(v.min()), 1), round(float(v.max()), 1))
                      for v in (arr[:, 0], arr[:, 1], arr[:, 2])]
            print(f"  {''.join(order)}: tv={tv:8.2f} resid={resid:.4f} "
                  f"ranges={ranges}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
