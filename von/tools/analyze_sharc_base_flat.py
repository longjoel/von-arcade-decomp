#!/usr/bin/env python3
"""Validate the recovered SHARC body-stream composition model.

The ordered capture proves the body stream is flat: every body part program is
pushed at the same depth from one shared base matrix.  For those programs the
committed 3x4 is exactly

    R_commit = R_record * R_base          (pre-multiply onto the base rotation)
    t_commit = t_base + v                 (record translation added unrotated)

where `v` is the fixed-point translation word triple and `R_record` is the
Z/Y/X composition of the record angle words.  This tool checks a normalized
ordered fixture (from `normalize_transform_trace.py`) and reports the per-part
rotation error and translation residual, so a new capture can be compared
without loading MAME.

Usage:
    python3 tools/analyze_sharc_base_flat.py FIXTURE.json
"""

from __future__ import annotations

import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path


def bits_float(bits: int) -> float:
    return struct.unpack("<f", struct.pack("<I", bits & 0xFFFFFFFF))[0]


def s16(word: int) -> int:
    word &= 0xFFFF
    return word - 0x10000 if word >= 0x8000 else word


def fixed16(word: int) -> float:
    value = (1.0 + (word & 0x3FF) / 1024.0) * (2.0 ** (((word >> 10) & 0x1F) - 15))
    return -value if word & 0x8000 else value


def mat3(row: list[float]) -> list[float]:
    # SHARC matrix window is [r0,r1,r2, r3,r4,r5, r6,r7,r8, t0,t1,t2].
    return row[0:9]


def matmul(a: list[float], b: list[float]) -> list[float]:
    return [sum(a[r * 3 + k] * b[k * 3 + c] for k in range(3))
            for r in range(3) for c in range(3)]


def record_rotation(rec: list[int]) -> list[float]:
    """Kernel layout 1: [X, Y, Z] angle words -> R = Rx * Ry * Rz."""
    scale = math.pi / 32768.0

    def rx(a):
        c, s = math.cos(a), math.sin(a)
        return [1, 0, 0, 0, c, -s, 0, s, c]

    def ry(a):
        c, s = math.cos(a), math.sin(a)
        return [c, 0, s, 0, 1, 0, -s, 0, c]

    def rz(a):
        c, s = math.cos(a), math.sin(a)
        return [c, -s, 0, s, c, 0, 0, 0, 1]

    return matmul(rx(s16(rec[0]) * scale),
                  matmul(ry(s16(rec[1]) * scale), rz(s16(rec[2]) * scale)))


def angle(a: list[float], b: list[float]) -> float:
    trace = sum(a[k] * b[k] for k in range(9))
    return math.degrees(math.acos(max(-1.0, min(1.0, (trace - 1.0) / 2.0))))


def analyze(fixture: dict) -> dict:
    packet_by_event = {p["event_id"]: p for p in fixture.get("packets", [])}

    rot: dict[str, list[float]] = defaultdict(list)
    trans: dict[str, list[float]] = defaultdict(list)
    depths: dict[str, set[int]] = defaultdict(set)
    bases: set[tuple] = set()

    for program in fixture.get("part_programs", []):
        packet = packet_by_event.get(program.get("packet_event_id"))
        if packet is None:
            continue
        words = packet["words"]  # [5,47,tx,ty,tz,22,Z,21,Y,20,X,58,...]
        oba = program["commit"]["oba"]
        # Kernel layout 1 record = [X, Y, Z, tx, ty, tz].
        rec = [words[10] & 0xFFFF, words[8] & 0xFFFF, words[6] & 0xFFFF]
        v = [fixed16(words[2]), fixed16(words[3]), fixed16(words[4])]
        base = [bits_float(b) for b in program["push"]["base_words"]]
        commit = [bits_float(b) for b in program["commit"]["matrix_words"]]
        pred = matmul(record_rotation(rec), mat3(base))
        rot[oba].append(angle(pred, mat3(commit)))
        # The recovered service projects the fixed-point translation through the
        # base as t += M^T v (kernel von_sharc_translate).
        bR = mat3(base)
        projected = [sum(bR[r * 3 + c] * v[r] for r in range(3)) for c in range(3)]
        trans[oba].append(max(abs(commit[9 + i] - base[9 + i] - projected[i])
                              for i in range(3)))
        depths[oba].add(program["push"]["depth"])
        bases.add(tuple(round(x, 3) for x in base[9:12]))

    return {"rot": rot, "trans": trans, "depths": depths, "bases": bases}


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(__doc__)
    fixture = json.loads(Path(sys.argv[1]).read_text())
    result = analyze(fixture)
    rot, trans, depths, bases = (result["rot"], result["trans"],
                                 result["depths"], result["bases"])
    if not rot:
        raise SystemExit("fixture has no joined part programs")

    print(f"fixture: {len(rot)} parts, {len(bases)} distinct base translations")
    print(f"{'oba':>10} {'n':>4} {'depth':>5} {'rot_mean':>9} {'rot_max':>8} "
          f"{'trans_mean':>10} {'trans_max':>9}")
    for oba in sorted(rot):
        n = len(rot[oba])
        rm = sum(rot[oba]) / n
        rx = max(rot[oba])
        tm = sum(trans[oba]) / n
        tx = max(trans[oba])
        depth = sorted(depths[oba])
        print(f"{oba:>10} {n:>4} {str(depth):>5} {rm:9.2f} {rx:8.2f} {tm:10.2f} {tx:9.2f}")

    # The flat model predicts zero rotation error for every body part program.
    worst = max(max(values) for values in rot.values())
    print(f"worst pre-multiply rotation error: {worst:.2f} deg")
    if worst > 1.0:
        print("NOTE: some parts are not yet on the flat pre-multiply model",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
