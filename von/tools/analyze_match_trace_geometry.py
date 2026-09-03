#!/usr/bin/env python3
"""Summarize the bounded host geometry streams in a post-start capture."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path

MATRIX = re.compile(r"vonj_geometry_matrix: (?:seq=\d+ )?time=([0-9.e+-]+) m=([^ ]+) t=([^ ]+)")
OBJECT = re.compile(r"vonj_geometry_object: (?:seq=\d+ )?time=([0-9.e+-]+) tpa=([0-9a-f]+) tha=([0-9a-f]+) oba=([0-9a-f]+) count=([0-9a-f]+) mode=(\d+) source=([^ ]+)(?: opcode=([0-9a-f]+))?")


def summarize(trace: Path, start_time: float, matrix_limit: int | None) -> dict[str, object]:
    matrix_count = object_count = attached = 0
    current_matrix: tuple[float, ...] | None = None
    sources: Counter[str] = Counter()
    opcodes: Counter[str] = Counter()
    timestamps: Counter[str] = Counter()
    obas: set[str] = set()
    identity_pairs: dict[str, set[tuple[str, str]]] = {}
    submissions: Counter[str] = Counter()
    matrices: set[tuple[float, ...]] = set()
    first_time = last_time = None
    for line in trace.read_text().splitlines():
        match = MATRIX.search(line)
        if match:
            matrix_count += 1
            current_matrix = tuple(float(v) for v in match[2].split(",")) + tuple(float(v) for v in match[3].split(","))
            if float(match[1]) >= start_time:
                matrices.add(current_matrix)
            continue
        match = OBJECT.search(line)
        if not match or float(match[1]) < start_time:
            continue
        time = float(match[1])
        object_count += 1
        attached += current_matrix is not None
        first_time = time if first_time is None else min(first_time, time)
        last_time = time if last_time is None else max(last_time, time)
        sources[match[7]] += 1
        opcodes[match[8] or "<absent>"] += 1
        timestamps[f"{time:.6f}"] += 1
        obas.add(match[4])
        identity_pairs.setdefault(match[4], set()).add((match[2], match[3]))
        submissions[match[4]] += 1
    multi_identity_obas = sum(len(pairs) > 1 for pairs in identity_pairs.values())
    return {
        "trace": str(trace),
        "start_time": start_time,
        "post_start_time_range": [first_time, last_time],
        "post_start_objects": object_count,
        "post_start_unique_oba": len(obas),
        "oba_with_stable_tpa_tha": sum(len(pairs) == 1 for pairs in identity_pairs.values()),
        "oba_with_multiple_tpa_tha": multi_identity_obas,
        "maximum_submissions_per_oba": max(submissions.values(), default=0),
        "post_start_objects_with_latest_matrix": attached,
        "post_start_matrices": len(matrices),
        "total_matrix_events": matrix_count,
        "matrix_stream_saturated": matrix_limit is not None and matrix_count >= matrix_limit,
        "objects_by_source": dict(sorted(sources.items())),
        "opcodes": dict(sorted(opcodes.items())),
        "objects_per_timestamp": {"count": len(timestamps), "minimum": min(timestamps.values(), default=0), "maximum": max(timestamps.values(), default=0)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--start-time", type=float, default=43.0)
    parser.add_argument("--matrix-limit", type=int)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    encoded = json.dumps(summarize(args.trace, args.start_time, args.matrix_limit), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
