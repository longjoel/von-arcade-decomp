#!/usr/bin/env python3
"""Find weapon/effect spawn events in a vonj geometry capture.

Splits each OBA's appearances into contiguous runs (an effect spawns, lives,
and disappears) and classifies by travel/speed, so missile/mine/beam/effect can
be told apart.
"""
import math, sys, collections
sys.path.insert(0, '/home/longjoel/Work/von-arcade-decomp/von/tools')
from export_geometry_frame_gltf import MATRIX, OBJECT

LOG = sys.argv[1]
MECH = {0x9e, 0xa1, 0xa4, 0x9f, 0xa6, 0xa7, 0xa8, 0xad, 0xae}
STAGE_MAX = 0x9d  # 0x80..0x9c are stage/ambient

cur = None
frames_by_oba = collections.defaultdict(dict)
for line in open(LOG, errors='ignore'):
    m = MATRIX.search(line)
    if m:
        cur = [float(x) for x in m.group(3).split(',')]
        continue
    m = OBJECT.search(line)
    if m and int(m[6]) == 3 and m[7] == 'polygon-rom':
        o = int(m[4], 16)
        fam = (o >> 16) & 0xff
        if fam not in MECH:
            frames_by_oba[o][round(float(m[1]) * 60)] = tuple(cur)

def runs(frames):
    ks = sorted(frames)
    out = []
    start = 0
    for i in range(1, len(ks) + 1):
        if i == len(ks) or ks[i] - ks[i - 1] > 5:
            if i - start >= 3:
                out.append(ks[start:i])
            start = i
    return out

def stats(rs, frames):
    travel = 0.0
    peak = 0.0
    for a, b in zip(rs, rs[1:]):
        d = math.dist(frames[a], frames[b])
        if d > 80:
            continue  # scene cut / teleport
        travel += d
        peak = max(peak, d / max(1, b - a))
    disp = math.dist(frames[rs[0]], frames[rs[-1]])
    return travel, peak, disp

events = collections.Counter()
for o, frames in frames_by_oba.items():
    for rs in runs(frames):
        if len(rs) < 3:
            continue
        span = rs[-1] - rs[0]
        travel, peak, disp = stats(rs, frames)
        if span > 200:
            continue  # long-lived: not a one-shot effect
        if peak > 60:
            continue  # teleport
        if peak > 6 and disp > 25:
            kind = "projectile"
        elif travel < 3:
            kind = "static"
        elif disp < 12:
            kind = "linger/effect"
        else:
            kind = "drift/effect"
        events[kind] += 1
        if kind in ("projectile",):
            print(f"{kind:10} oba={o:08x} span={span:4d} travel={travel:8.1f} peak={peak:6.1f} disp={disp:7.1f}")

print()
print("event kinds:", dict(events))
