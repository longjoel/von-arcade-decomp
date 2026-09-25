#!/usr/bin/env python3
"""Drop non-player draws of shared parts from a geometry trace.

A player-only capture (`VON_ONLY_OBAS`) removes the other fighter's unique
parts, but any part the two fighters share (e.g. Apharmd borrowing Temjin's
hands) is still submitted by both, at each entity's pose. The entity cannot be
told apart by OBA; the player's draw is the one consistent with the player's
root, so for every frame each repeated OBA keeps only the submission whose
translation is nearest that frame's root.

The player is selected by the fighter's root OBA; `--instance` picks the nth
root when the enemy is a mirror (Temjin vs Temjin) and shares it.

  python3 tools/filter_player_trace.py --trace in --root 00a7f213 --out out
"""

from __future__ import annotations

import argparse
import math
import re
from collections import defaultdict
from pathlib import Path

MATRIX = re.compile(r"vonj_geometry_matrix: (?:seq=\d+ )?time=([0-9.e+-]+) "
                    r"m=([^ ]+) t=([^ ]+)")
OBJECT = re.compile(r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+) "
                    r".*?oba=([0-9a-f]{8})")


def filter_trace(source: Path, root: str, instance: int, out: Path) -> dict:
    records = []  # (obj_index, time_key, oba, translation)
    current = (0.0, 0.0, 0.0)
    with source.open(errors="ignore") as stream:
        for line in stream:
            matrix = MATRIX.search(line)
            if matrix:
                current = tuple(float(v) for v in matrix.group(3).split(","))
                continue
            obj = OBJECT.search(line)
            if obj:
                records.append((len(records), round(float(obj.group(1)), 3),
                                obj.group(2), current))

    frames: dict[float, list] = defaultdict(list)
    for record in records:
        frames[record[1]].append(record)

    drop: set[int] = set()
    shared = 0
    for entries in frames.values():
        roots = [r for r in entries if r[2] == root]
        if not roots:
            continue
        anchor = roots[min(instance, len(roots) - 1)][3]
        by_oba: dict[str, list] = defaultdict(list)
        for record in entries:
            by_oba[record[2]].append(record)
        for drawn in by_oba.values():
            if len(drawn) < 2:
                continue
            keep = min(drawn, key=lambda r: math.dist(r[3], anchor))
            for record in drawn:
                if record is not keep:
                    drop.add(record[0])
                    shared += 1

    obj_index = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    with source.open(errors="ignore") as stream, out.open("w") as sink:
        for line in stream:
            if OBJECT.search(line):
                if obj_index not in drop:
                    sink.write(line)
                obj_index += 1
            else:
                sink.write(line)
    return {"objects": obj_index, "dropped": len(drop), "repeat_draws": shared}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--root", required=True)
    parser.add_argument("--instance", type=int, default=0)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    report = filter_trace(args.trace, args.root.lower(), args.instance, args.out)
    print(f"filtered {args.trace} -> {args.out}: "
          f"{report['objects']} objects, {report['dropped']} dropped, "
          f"{report['repeat_draws']} repeat draws")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
