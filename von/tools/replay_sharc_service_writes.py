#!/usr/bin/env python3
"""Replay raw SHARC matrix writes without assuming service arithmetic."""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


def f32(word: int) -> float:
    return struct.unpack("<f", struct.pack("<I", word & 0xffffffff))[0]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--frame", type=int, required=True)
    parser.add_argument("--check", action="store_true",
                        help="fail if reconstructed live memory differs from commit")
    args = parser.parse_args()
    matrices = {}
    active = {}
    reports = []
    for line in args.trace.open():
        e = json.loads(line)
        if e.get("frame") != args.frame:
            continue
        kind = e.get("kind")
        if kind == "push":
            matrices[e["pointer"]] = list(e["base_words"])
            active[e["depth"]] = e["pointer"]
        elif kind == "pop":
            active.pop(e.get("depth"), None)
        elif kind == "sharc_service_write":
            pointer = e.get("pointer") or active.get(e.get("depth"))
            if pointer not in matrices:
                continue
            index = e["offset"] - pointer
            if 0 <= index < 12:
                matrices[pointer][index] = e["data"]
        elif kind == "commit":
            pointer = active.get(e.get("depth"))
            reports.append({"event_id": e["event_id"],
                            "destination": e["destination"],
                            "commit": [f32(x) for x in e["matrix_words"]],
                            "live_candidates": [
                                {"pointer": p, "matrix": [f32(x) for x in m]}
                                for p, m in matrices.items()],
                            "active_pointer": pointer,
                            "active_matrix": ([f32(x) for x in matrices[pointer]]
                                               if pointer in matrices else None)})
    if args.check:
        missing = sum(r["active_matrix"] is None for r in reports)
        mismatches = [r for r in reports
                      if r["active_matrix"] is not None and
                      any(abs(a - b) > 1e-6
                          for a, b in zip(r["active_matrix"], r["commit"]))]
        if mismatches:
            print(json.dumps({"commits": len(reports),
                              "missing": missing,
                              "mismatches": len(mismatches)}, separators=(",", ":")))
            return 1
        print(json.dumps({"commits": len(reports), "missing": missing,
                          "mismatches": 0},
                         separators=(",", ":")))
        return 0
    print(json.dumps(reports, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
