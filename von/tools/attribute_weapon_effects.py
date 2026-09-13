#!/usr/bin/env python3
"""Attribute effect OBA families to mech weapon-mount parts in a geometry capture.

`classify_weapon_effects.py` splits each OBA's appearances into contiguous spawn
runs and classes them by motion. This tool adds the other half of the mapping:
for every non-mech run it finds the nearest persistent mech part at the spawn
frame, so a projectile or muzzle-flash family can be tied to the mount that
fired it. Optionally it labels the mount left/center/right from the cross
product of the mount offset with the effect's travel direction.

Geometry log grammar and the `MATRIX`/`OBJECT` regexes live in
`export_geometry_frame_gltf.py`.

    python3 von/tools/attribute_weapon_effects.py <capture.log> [--json out.json]
"""
from __future__ import annotations

import argparse
import collections
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from export_geometry_frame_gltf import MATRIX, OBJECT  # noqa: E402

# Registry-confirmed fighter bodies (von/oba_registry.json).
MECH = {
    0x9E: "Temjin", 0xA1: "Viper2", 0xA4: "Belgador", 0x9F: "Raiden",
    0xA6: "Dorkas", 0xA8: "FeiYen", 0xA7: "Apharmd", 0xAD: "BalBasBow",
    0xAE: "UnknownAE",
}
# Stage / menu / arena families that are not per-shot effects.
STAGE = {0x80, 0x84, 0x85, 0x93}


def parse_log(path: Path):
    """Return {oba: {frame: (x, y, z)}} for every polygon-rom mode-3 object."""
    current = None
    frames_by_oba: dict[int, dict[int, tuple[float, float, float]]] = collections.defaultdict(dict)
    with path.open(errors="ignore") as handle:
        for line in handle:
            matrix = MATRIX.search(line)
            if matrix:
                current = tuple(float(value) for value in matrix.group(3).split(","))
                continue
            match = OBJECT.search(line)
            if match and int(match.group(6)) == 3 and match.group(7).rstrip() == "polygon-rom":
                oba = int(match.group(4), 16)
                frames_by_oba[oba][round(float(match.group(1)) * 60)] = current
    return frames_by_oba


def split_runs(frames: dict, gap: int = 5, min_len: int = 2):
    """Split a frame->position map into contiguous appearance runs."""
    keys = sorted(frames)
    runs = []
    start = 0
    for index in range(1, len(keys) + 1):
        if index == len(keys) or keys[index] - keys[index - 1] > gap:
            if index - start >= min_len:
                runs.append(keys[start:index])
            start = index
    return runs


def classify_run(rs: list[int], frames: dict) -> tuple[str, float, float, float]:
    """Classify one run as projectile / static / linger / drift, with stats."""
    travel = 0.0
    peak = 0.0
    for a, b in zip(rs, rs[1:]):
        distance = math.dist(frames[a], frames[b])
        if distance > 80:  # scene cut / teleport
            continue
        travel += distance
        peak = max(peak, distance / max(1, b - a))
    disp = math.dist(frames[rs[0]], frames[rs[-1]])
    if peak > 6 and disp > 25:
        return "projectile", travel, peak, disp
    if travel < 3:
        return "static", travel, peak, disp
    if disp < 12:
        return "linger", travel, peak, disp
    return "drift", travel, peak, disp


def _base_parts(frames_by_oba: dict, base_frac: float) -> set[int]:
    total = max((max(frames) for frames in frames_by_oba.values() if frames), default=0)
    base = set()
    for oba, frames in frames_by_oba.items():
        if (oba >> 16) & 0xFF in MECH and len(frames) / max(1, total) >= base_frac:
            base.add(oba)
    return base


def _median(values: list[float]) -> float:
    ordered = sorted(values)
    return ordered[len(ordered) // 2] if ordered else 0.0


def _side_label(fwd, mount, centroid) -> str:
    """Left/center/right of the mount offset relative to the fire direction."""
    def sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
    def dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
    def cross(a, b): return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])
    def norm(a):
        length = math.sqrt(dot(a, a)) or 1.0
        return (a[0] / length, a[1] / length, a[2] / length)
    right = norm(cross(norm(fwd), (0.0, 1.0, 0.0)))
    offset = dot(sub(mount, centroid), right)
    return "R" if offset > 3 else "L" if offset < -3 else "C"


def build_report(frames_by_oba: dict, base_frac: float = 0.05, sides: bool = False) -> dict:
    base_parts = _base_parts(frames_by_oba, base_frac)
    mech_frames: dict[int, list[tuple[int, int, tuple]]] = collections.defaultdict(list)
    for oba in base_parts:
        fam = (oba >> 16) & 0xFF
        for frame, pos in frames_by_oba[oba].items():
            mech_frames[frame].append((fam, oba, pos))

    report: dict[str, dict] = {}
    for oba, frames in frames_by_oba.items():
        fam = (oba >> 16) & 0xFF
        if fam in MECH or fam in STAGE:
            continue
        entry = report.setdefault(f"{fam:02x}", {
            "runs": 0, "classes": collections.Counter(),
            "mounts": collections.Counter(), "mount_dist": collections.defaultdict(list),
            "mount_sides": collections.Counter(),
            "mechfam": collections.Counter(),
        })
        for rs in split_runs(frames):
            kind, _travel, _peak, disp = classify_run(rs, frames)
            entry["runs"] += 1
            entry["classes"][kind] += 1
            spawn = rs[0]
            best = None
            for frame in (spawn, spawn + 1, spawn + 2):
                for (mech_fam, mech_oba, pos) in mech_frames.get(frame, []):
                    distance = math.dist(frames[spawn], pos)
                    if best is None or distance < best[0]:
                        best = (distance, mech_fam, mech_oba, frame)
            if best is None:
                continue
            distance, mech_fam, mech_oba, frame = best
            key = f"{mech_fam:02x}:{mech_oba:08x}"
            entry["mounts"][key] += 1
            entry["mount_dist"][key].append(distance)
            entry["mechfam"][f"{mech_fam:02x}"] += 1
            if sides and disp > 25:
                centroid_points = [
                    pos for (mf, _mo, pos) in mech_frames.get(frame, []) if mf == mech_fam
                ]
                if centroid_points:
                    centroid = (
                        _median([p[0] for p in centroid_points]),
                        _median([p[1] for p in centroid_points]),
                        _median([p[2] for p in centroid_points]),
                    )
                    label = _side_label(
                        tuple(b - a for a, b in zip(frames[spawn], frames[rs[-1]])),
                        frames_by_oba[mech_oba][frame], centroid,
                    )
                    entry["mount_sides"][f"{key}:{label}"] += 1

    out = {}
    for fam, entry in sorted(report.items()):
        out[fam] = {
            "runs": entry["runs"],
            "classes": dict(entry["classes"]),
            "mechfam": dict(entry["mechfam"]),
            "mounts": [
                {"mount": key, "count": count,
                 "median_dist": round(_median(entry["mount_dist"][key]), 1)}
                for key, count in entry["mounts"].most_common(8)
            ],
            "mount_sides": dict(entry["mount_sides"]),
        }
    return out


def format_report(report: dict) -> str:
    lines = [
        f"{'fam':>4} {'runs':>5} {'proj':>5} {'ling':>5} {'stat':>5} {'drift':>5}  mechfam -> top mounts",
    ]
    for fam, entry in report.items():
        classes = entry["classes"]
        mounts = " ".join(
            f"{m['mount']}({m['count']},{m['median_dist']})" for m in entry["mounts"][:5]
        )
        mechfam = " ".join(f"{k}:{v}" for k, v in entry["mechfam"].items())
        lines.append(
            f"{fam:>4} {entry['runs']:>5} {classes.get('projectile', 0):>5} "
            f"{classes.get('linger', 0):>5} {classes.get('static', 0):>5} "
            f"{classes.get('drift', 0):>5}  [{mechfam}] {mounts}"
        )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--json", type=Path)
    parser.add_argument("--base-frac", type=float, default=0.05,
                        help="minimum frame presence to count as a persistent mech part")
    parser.add_argument("--sides", action="store_true",
                        help="also estimate left/center/right from the travel direction")
    args = parser.parse_args()

    report = build_report(parse_log(args.log), args.base_frac, args.sides)
    print(format_report(report))
    if args.json:
        args.json.write_text(json.dumps(report, indent=1) + "\n")
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
