#!/usr/bin/env python3
"""Verify the runtime normal-branch contrast for opcode 0x17."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--probe-log", type=Path, required=True)
    args = parser.parse_args()

    probe = args.probe_log.read_text(encoding="utf-8", errors="replace")
    if "probe: contrast record normal fixture, query=(0,0)" not in probe:
        raise SystemExit("normal contrast probe marker missing")

    trace = args.trace.read_text(encoding="utf-8", errors="replace")
    normal = trace.count("vonj_sharc_20de1_step: pc=020e4d ")
    sentinel = trace.count("vonj_sharc_20de1_step: pc=020e50 ")
    if (normal, sentinel) != (2, 0):
        raise SystemExit(
            f"unexpected contrast helper branches: normal={normal} sentinel={sentinel}"
        )

    outputs = re.findall(
        r"vonj_sharc_output: pc=0203[0-9a-f]{2} address=00c00000 data=([0-9a-f]+)",
        trace,
    )
    expected = ["00000002", "bcdd67c8", "00000000", "bf7fffff", "00000001"]
    if outputs[-5:] != expected:
        raise SystemExit(f"unexpected contrast output words: {outputs[-5:]}")

    print("PASS: opcode-0x17 prevalidation normal contrast")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
