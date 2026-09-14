#!/usr/bin/env python3
"""Validate the SHARC motion-record transform against a geometry trace.

Reads a joint `VON_TRACE` geometry + `VON_EMITTER` capture log, decodes the
per-part packet protocol [push(5), translate(2f)+3, Z(16), Y(15), X(14),
commit(3a), pop(6)], runs the model in `sharc_transform.compose_motion_record`,
and reports the rotation error of `W_parent * L_child` against the logged
`vonj_geometry_matrix` (paired by OBA via emitter-g2-oba.json).

Usage:
  python3 von/tools/validate_sharc_composition.py --log <error.log> \
      [--t0 20.219] [--t1 20.220] [--mat-t0 20.234] [--mat-t1 20.236]

The capture is made with, e.g.:
  VON_TRACE_T0=20 VON_TRACE_T1=32 VON_EMITTER_T0=20 VON_EMITTER_T1=32 \
    bin/von vonj -rompath ... -log -oslog -autoboot_script ...
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sharc_transform as st  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
G2_OBA = ROOT / "von/i960/emitter-g2-oba.json"

EMIT = re.compile(r"vonj_emitter: time=([\d.]+) pc=(\w+) data=(\w+) r6=(\w+) g0=(\w+) g2=(\w+)")
OBJ = re.compile(r"vonj_geometry_object: time=([\d.]+) tpa=(\w+) tha=(\w+) oba=(\w+)")
MAT = re.compile(r"vonj_geometry_matrix: time=([\d.]+) m=([-\d.,]+) t=([-\d.,]+)")


def matmul3(a, b):
    return [sum(a[r * 3 + c] * b[c * 3 + col] for c in range(3))
            for r in range(3) for col in range(3)]


def inv3(a):
    x, y, z, u, v, w, p, q, r = a
    det = x * (v * r - w * q) - y * (u * r - w * p) + z * (u * q - v * p)
    return [(v * r - w * q) / det, (z * q - y * r) / det, (y * w - z * v) / det,
            (w * p - u * r) / det, (x * r - z * p) / det, (z * u - x * w) / det,
            (u * q - v * p) / det, (y * p - x * q) / det, (x * v - y * u) / det]


def angle(a):
    return math.degrees(math.acos(max(-1.0, min(1.0, (a[0] + a[4] + a[8] - 1) / 2))))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--log", required=True, type=Path)
    ap.add_argument("--t0", type=float, default=20.2190)
    ap.add_argument("--t1", type=float, default=20.2200)
    ap.add_argument("--mat-t0", type=float, default=20.2340)
    ap.add_argument("--mat-t1", type=float, default=20.2360)
    args = ap.parse_args()

    g2oba = json.loads(G2_OBA.read_text())
    writes, objs, mats = [], [], []
    for line in args.log.open(errors="ignore"):
        if "vonj_emitter" in line:
            m = EMIT.search(line)
            if m and args.t0 <= float(m.group(1)) <= args.t1:
                writes.append((int(m.group(3), 16), m.group(6)))
        elif "vonj_geometry_object" in line:
            m = OBJ.search(line)
            if m and args.mat_t0 <= float(m.group(1)) <= args.mat_t1:
                objs.append(m.group(4))
        elif "vonj_geometry_matrix" in line:
            m = MAT.search(line)
            if m and args.mat_t0 <= float(m.group(1)) <= args.mat_t1:
                mats.append(([float(x) for x in m.group(2).split(",")],
                             [float(x) for x in m.group(3).split(",")]))

    packets = {}
    i = 0
    while i + 12 < len(writes):
        w = writes
        if w[i][0] == 5 and w[i + 1][0] == 0x2F and w[i + 5][0] == 0x16 \
                and w[i + 7][0] == 0x15 and w[i + 9][0] == 0x14 and w[i + 11][0] == 0x3A:
            packets[w[i][1]] = [w[i + 2][0], w[i + 3][0], w[i + 4][0],
                                w[i + 6][0], w[i + 8][0], w[i + 10][0]]
            i += 12
        else:
            i += 1

    world = {}
    for k, o in enumerate(objs):
        if k < len(mats) and o not in world:
            world[o] = mats[k]

    model = {}
    for g2, rec in packets.items():
        oba = g2oba.get(g2)
        if oba:
            model[g2] = st.compose_motion_record(rec, None) + (oba,)

    keys = [g for g in model if model[g][2] in world]
    print(f"packets={len(packets)} objects={len(objs)} matrices={len(mats)} paired={len(keys)}")
    if len(keys) < 2:
        return 1

    best = []
    for p in keys:
        _, _, op = model[p]
        wp = world[op][1]
        for c in keys:
            if c == p:
                continue
            mc, tc, oc = model[c]
            pred_r = matmul3(world[op][0], mc)
            rerr = angle(matmul3(inv3(pred_r), world[oc][0]))
            best.append((rerr, p, c, wp))
    best.sort()
    for rerr, p, c, _ in best[:8]:
        print(f"  W[{p}]*L[{c}] rot_err={rerr:6.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
