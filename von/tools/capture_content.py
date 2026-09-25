#!/usr/bin/env python3
"""Content assertions for geometry action-capture traces.

`capture_manifest.py` validates the bundle *structure* (hashes, isolation,
inputs). It cannot tell a trace that reached the match from a partial or
stalled run that only pumped NOP opcodes. These helpers do: they require the
geometry submission events, and optionally the labelled action windows, before
a trace may be registered as canonical.
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


ACTION_RE = re.compile(r"action: t=([\d.]+) frame=\d+ action=(\w+) (begin|end)")
OBJECT_RE = re.compile(r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+)")
MATRIX_RE = re.compile(r"vonj_geometry_matrix: (?:seq=\d+ )?time=([0-9.e+-]+)")
OBA_RE = re.compile(r"oba=([0-9a-f]+)")

DEFAULT_ACTIONS = (
    "idle", "forward", "back", "strafe_left", "strafe_right", "turn_left",
    "turn_right", "dash_forward", "guard", "jump", "shot_left", "shot_right",
)


def scan_trace(path: Path) -> dict:
    """Count geometry events and collect the object OBA bank."""
    counts: Counter[str] = Counter()
    obas: set[str] = set()
    first_time: float | None = None
    last_time: float | None = None
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if "vonj_geometry_object" in line:
                counts["vonj_geometry_object"] += 1
                match = OBJECT_RE.search(line)
                if match:
                    time = float(match.group(1))
                    first_time = time if first_time is None else first_time
                    last_time = time
                oba = OBA_RE.search(line)
                if oba:
                    obas.add(oba.group(1))
            elif "vonj_geometry_matrix" in line:
                counts["vonj_geometry_matrix"] += 1
            elif "vonj_geometry_polygon" in line:
                counts["vonj_geometry_polygon"] += 1
            elif "vonj_copro_fifo" in line:
                counts["vonj_copro_fifo"] += 1
    return {"counts": dict(counts), "obas": sorted(obas),
            "first_time": first_time, "last_time": last_time}


def labelled_actions(path: Path) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = ACTION_RE.search(line)
        if match:
            name = match.group(2)
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def verify_content(trace: Path, *, actions: Path | None = None,
                   min_objects: int = 1, min_matrices: int = 1,
                   require_obas: tuple[str, ...] = (),
                   expected_actions: tuple[str, ...] = ()) -> tuple[dict, list[str]]:
    errors: list[str] = []
    if not trace.is_file():
        return {}, [f"missing trace {trace}"]
    report = scan_trace(trace)
    counts = report["counts"]
    if counts.get("vonj_geometry_object", 0) < min_objects:
        errors.append(
            f"trace has {counts.get('vonj_geometry_object', 0)} geometry objects "
            f"(need >= {min_objects}); run did not reach the geometry engine")
    if counts.get("vonj_geometry_matrix", 0) < min_matrices:
        errors.append(
            f"trace has {counts.get('vonj_geometry_matrix', 0)} geometry matrices "
            f"(need >= {min_matrices})")
    missing_obas = [oba.lower() for oba in require_obas
                    if oba.lower() not in report["obas"]]
    if missing_obas:
        errors.append("trace is missing required OBAs: " + ", ".join(missing_obas))
    if expected_actions:
        if actions is None or not actions.is_file():
            errors.append("action log missing; cannot confirm labelled windows")
        else:
            present = set(labelled_actions(actions))
            missing = [name for name in expected_actions if name not in present]
            if missing:
                errors.append("trace is missing action windows: " + ", ".join(missing))
    return report, errors


def normalize_lines(path: Path):
    """Yield trace lines with host wall-clock noise removed."""
    with path.open(encoding="utf-8", errors="replace") as stream:
        for line in stream:
            if line.startswith("Average speed:"):
                continue
            yield line


def compare_traces(reference: Path, candidate: Path) -> str | None:
    """Return the first divergence between two traces, or None if equal."""
    left = normalize_lines(reference)
    right = normalize_lines(candidate)
    line = 0
    while True:
        a = next(left, None)
        b = next(right, None)
        line += 1
        if a is None and b is None:
            return None
        if a != b:
            return (f"first divergence at line {line}:\n"
                    f"  reference: {a!r}\n"
                    f"  candidate: {b!r}")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--actions", type=Path)
    parser.add_argument("--min-objects", type=int, default=1)
    parser.add_argument("--min-matrices", type=int, default=1)
    parser.add_argument("--require-oba", action="append", default=[])
    parser.add_argument("--expect-action", action="append", default=[])
    parser.add_argument("--compare", type=Path,
                        help="second trace to diff, ignoring the speed line")
    args = parser.parse_args()
    expected = tuple(args.expect_action) if args.expect_action else DEFAULT_ACTIONS
    report, errors = verify_content(
        args.trace, actions=args.actions, min_objects=args.min_objects,
        min_matrices=args.min_matrices, require_obas=tuple(args.require_oba),
        expected_actions=expected)
    print(f"geometry objects={report.get('counts', {}).get('vonj_geometry_object', 0)} "
          f"matrices={report.get('counts', {}).get('vonj_geometry_matrix', 0)} "
          f"obas={len(report.get('obas', []))}")
    if args.compare is not None:
        divergence = compare_traces(args.trace, args.compare)
        if divergence:
            errors.append(divergence)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("valid capture content")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
