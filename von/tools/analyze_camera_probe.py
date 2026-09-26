#!/usr/bin/env python3
"""Summarize a camera probe state dump (`probe_camera.lua` + VON_CAMERA_STATE).

Each `f<frame> state <u32...>` line is a raw work-RAM dump starting at
0x503ad8. This reads the recovered camera cells (von/i960/recovered-camera.md)
and the fighter positions, then reports the base camera pose and the
close/lock pose so motion- and stage-dependent changes are visible.

    python3 von/tools/analyze_camera_probe.py von/build/motion-base/stage0/*.lua.log
    python3 von/tools/analyze_camera_probe.py --far-range 150 --from-frame 2600 <log>

Cells (word index from 0x503ad8):
    0/1/2      player x/y/z
    384/385/386 opponent x/y/z
    1072..1074 camera eye
    1079..1081 camera target
Note: 0x504bc8 is a duplicate of the target z, not a usable distance cell; the
effective camera distance is |eye - target| on the horizontal plane.
"""
from __future__ import annotations

import argparse
import glob
import math
import statistics
import struct
from pathlib import Path

BASE = 0x503AD8
PLAYER = (0, 1, 2)
ENEMY = (384, 385, 386)
EYE = (1072, 1073, 1074)
TARGET = (1079, 1080, 1081)


def _f32(word: int) -> float:
    return struct.unpack("<f", struct.pack("<I", word & 0xFFFFFFFF))[0]


def parse_log(path: Path):
    rows = []
    for line in path.read_text(errors="ignore").splitlines():
        if " state " not in line:
            continue
        parts = line.split()
        try:
            frame = int(parts[0][1:])
        except ValueError:
            continue
        words = [int(word, 16) for word in parts[2:]]

        def at(index: int) -> float:
            return _f32(words[index]) if index < len(words) else 0.0

        player = [at(i) for i in PLAYER]
        enemy = [at(i) for i in ENEMY]
        eye = [at(i) for i in EYE]
        target = [at(i) for i in TARGET]
        rows.append({"frame": frame, "player": player, "enemy": enemy,
                     "eye": eye, "target": target})
    return rows


def _pose(rows):
    if not rows:
        return None
    def med(values):
        return statistics.median(values)
    eye_y = [r["eye"][1] for r in rows]
    target_y = [r["target"][1] for r in rows]
    horiz = [math.hypot(r["eye"][0] - r["target"][0],
                        r["eye"][2] - r["target"][2]) for r in rows]
    return {"n": len(rows), "eye_y": med(eye_y), "target_y": med(target_y),
            "distance": med(horiz), "offset": med(eye_y) - med(target_y)}


def _fmt(label, pose):
    if pose is None:
        return f"{label}: none"
    return (f"{label}: n={pose['n']:5d} eye_y={pose['eye_y']:.2f} "
            f"target_y={pose['target_y']:.2f} distance={pose['distance']:.2f} "
            f"vertical_offset={pose['offset']:.2f}")


def _range(row) -> float:
    return math.hypot(row["player"][0] - row["enemy"][0],
                      row["player"][2] - row["enemy"][2])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+")
    parser.add_argument("--from-frame", type=int, default=0,
                        help="ignore frames before this")
    parser.add_argument("--grounded", action="store_true",
                        help="keep only frames with player y ~ 0")
    parser.add_argument("--far-range", type=float, default=0.0,
                        help="keep only player-enemy range above this")
    parser.add_argument("--near-range", type=float, default=0.0,
                        help="report this close window separately")
    args = parser.parse_args()

    paths = []
    for pattern in args.logs:
        matched = glob.glob(pattern)
        paths.extend(Path(p) for p in (matched or [pattern]))

    worst = 0
    for path in paths:
        rows = parse_log(path)
        if not rows:
            print(f"{path}: no state lines")
            worst = 1
            continue
        rows = [r for r in rows if r["frame"] >= args.from_frame]
        if args.grounded:
            rows = [r for r in rows if abs(r["player"][1]) < 0.01]
        if args.far_range > 0:
            rows = [r for r in rows if _range(r) > args.far_range]
        if args.near_range > 0:
            near = [r for r in rows if _range(r) < args.near_range]
            far = [r for r in rows if _range(r) >= args.near_range]
            print(f"{path}")
            print("  " + _fmt(f"far (>={args.near_range:g})", _pose(far)))
            print("  " + _fmt(f"close (<{args.near_range:g})", _pose(near)))
        else:
            print(_fmt(str(path), _pose(rows)))
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
