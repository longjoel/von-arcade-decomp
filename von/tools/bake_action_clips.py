#!/usr/bin/env python3
"""Bake per-state animation clips from a labelled action capture.

Reads the action log written by `von/tools/action_schedule.lua` and the paired
geometry trace, trims each action window to its steady middle, bakes one clip
per action via `bake_fighter_animation.py`, and prints the
`rig_to_header_multi.py` command that combines them into a kernel clip table.

Usage:
  bake_action_clips.py --trace action.trace --actions action.actions.log \
      --parts .../Temjin.parts.json --fighter Temjin --out-dir build/action-clips/temjin

The action -> slot map is fixed here so the kernel's state selection stays in
sync: 0 idle, 1 walk, 2 dash, 3 attack-left, 4 attack-center, 5 attack-right,
6 hit/knockdown.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# action label -> kernel slot. First match wins when several windows exist.
SLOTS = {
    "idle": 0,
    "up": 1,
    "down": 1,
    "right": 1,
    "left": 1,
    "left_dash": 2,
    "right_dash": 2,
    "left_shot": 3,
    "right_shot": 5,
}
BEGIN = re.compile(r"action: t=([\d.]+) frame=\d+ action=(\w+) begin")
END = re.compile(r"action: t=([\d.]+) frame=\d+ action=(\w+) end")
# Fraction of each window dropped at the edges so the baked clip is the steady
# action, not the transition into/out of it.
TRIM_HEAD = 0.25
TRIM_TAIL = 0.25


def windows(log: Path):
    open_windows: list[list] = []
    for line in log.read_text(encoding="utf-8").splitlines():
        b = BEGIN.match(line)
        e = END.match(line)
        if b:
            open_windows.append([b.group(2), float(b.group(1)), None])
        elif e and open_windows and open_windows[-1][0] == e.group(2):
            open_windows[-1][2] = float(e.group(1))
    return [w for w in open_windows if w[2] is not None]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--trace", type=Path, required=True)
    ap.add_argument("--actions", type=Path, required=True)
    ap.add_argument("--parts", type=Path, required=True)
    ap.add_argument("--fighter", required=True)
    ap.add_argument("--out-dir", type=Path, required=True)
    ap.add_argument("--match", choices=("oba", "tpa"), default="oba")
    a = ap.parse_args()

    a.out_dir.mkdir(parents=True, exist_ok=True)
    chosen: dict[int, Path] = {}
    commands = [f"{a.fighter}:{hint}" for hint in ("idle", "active")]
    for name, t0, t1 in windows(a.actions):
        if name not in SLOTS:
            continue
        slot = SLOTS[name]
        if slot in chosen:
            continue  # first window of each action is enough
        span = t1 - t0
        b = t0 + span * TRIM_HEAD
        e = t1 - span * TRIM_TAIL
        out = a.out_dir / f"{a.fighter.lower()}_{name}.json"
        subprocess.run([
            sys.executable, str(HERE / "bake_fighter_animation.py"),
            "--trace", str(a.trace), "--fighter", a.fighter,
            "--parts", str(a.parts), "--match", a.match,
            "--t0", f"{b:.3f}", "--t1", f"{e:.3f}", "--out", str(out),
        ], check=True)
        chosen[slot] = out
        print(f"slot {slot}: {name} -> {out.name}")

    spec = " ".join(f"{a.fighter}:{slot}={path}" for slot, path in sorted(chosen.items()))
    print("\nCombine into the kernel table, e.g.:\n"
          f"  python3 {HERE / 'rig_to_header_multi.py'} --slots 6 "
          f"--out native/kernels/fighter_anims.h <other fighters...> {spec}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
