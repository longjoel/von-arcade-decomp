#!/usr/bin/env python3
"""Verify the controlled simple-plane opcode-0x17 sentinel capture."""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--probe-log", type=Path, required=True)
    args = parser.parse_args()

    probe = args.probe_log.read_text(encoding="utf-8", errors="replace")
    expected_cases = [
        "probe: case=1 base P2=(1,1,0)",
        "probe: case=2 P2=(1,2,0)",
        "probe: case=3 P3=(0,1,1)",
        "probe: case=4 P1=(2,1,0)",
    ]
    if [line for line in probe.splitlines() if line.startswith("probe: case=")] != expected_cases:
        raise SystemExit("sentinel geometry probe cases changed")

    # The four fixture records all have nonzero plane Y-normals. This keeps
    # the captured sentinel distinct from the ordinary zero-Y-normal division
    # degeneracy modeled by recovered_sharc_helper_20de1.c.
    records = [
        ((0, 0, 0), (2, 0, 0), (1, 1, 0), (0, 0, 1)),
        ((0, 0, 0), (2, 0, 0), (1, 2, 0), (0, 0, 1)),
        ((0, 0, 0), (2, 0, 0), (1, 1, 0), (0, 1, 1)),
        ((0, 0, 0), (2, 1, 0), (1, 1, 0), (0, 0, 1)),
    ]
    normals_y = []
    for p0, p1, p2, p3 in records:
        u = tuple(p2[i] - p0[i] for i in range(3))
        v = tuple(p3[i] - p0[i] for i in range(3))
        normals_y.append(u[2] * v[0] - u[0] * v[2])
    if any(math.isclose(value, 0.0) for value in normals_y):
        raise SystemExit(f"sentinel fixture contains a zero Y-normal: {normals_y}")

    trace = args.trace.read_text(encoding="utf-8", errors="replace")
    entries = trace.count("vonj_sharc_20de1_step: pc=020de1 ")
    sentinels = trace.count("vonj_sharc_20de1_step: pc=020e50 ")
    normals = trace.count("vonj_sharc_20de1_step: pc=020e4d ")
    if (entries, sentinels, normals) != (4, 4, 0):
        raise SystemExit(
            f"unexpected helper branches: entries={entries} "
            f"sentinels={sentinels} normals={normals}"
        )

    e32_f2 = re.findall(
        r"vonj_sharc_20de1_step: pc=020e32 .*?f2=([0-9a-f]+)", trace
    )
    if e32_f2[-4:] != ["00000000"] * 4:
        raise SystemExit(f"sentinel cases do not share the early F2 equality: {e32_f2[-4:]}")

    outputs = re.findall(
        r"vonj_sharc_output: pc=020387 address=00c00000 data=([0-9a-f]+)",
        trace,
    )
    if outputs[-4:] != ["bdcccccd"] * 4:
        raise SystemExit(f"unexpected sentinel result words: {outputs[-4:]}")
    selected = re.findall(
        r"vonj_sharc_output: pc=02038c address=00c00000 data=([0-9a-f]+)",
        trace,
    )
    if selected[-4:] != ["00000000"] * 4:
        raise SystemExit(f"unexpected selected-record words: {selected[-4:]}")

    print("PASS: controlled opcode-0x17 sentinel geometry capture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
