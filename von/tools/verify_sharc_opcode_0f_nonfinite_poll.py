#!/usr/bin/env python3
"""Verify direct FIFO results from the opcode-0x0f nonfinite probe."""

from __future__ import annotations

import re
import sys
import argparse
from pathlib import Path


INTERPRETER_EXPECTED = [0x80000000, 0x80000000, 0x00003FFF, 0x00000000,
                        0x00000000, 0x00003FFF, 0xFFFFC000, 0x80000000]
# The DRC path used to diverge on the two NaN vectors.  Canonical-NaN
# writeback now makes both engines produce the same stream.
DRC_EXPECTED = INTERPRETER_EXPECTED
PATTERN = re.compile(r"response-poll=(\d+) vector-index=(\d+)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("poll_log", type=Path)
    parser.add_argument("--engine", choices=("interpreter", "drc"), default="interpreter")
    args = parser.parse_args()
    expected = INTERPRETER_EXPECTED if args.engine == "interpreter" else DRC_EXPECTED
    results = {}
    for line in args.poll_log.read_text(encoding="utf-8").splitlines():
        match = PATTERN.search(line)
        if match:
            value, index = (int(group) for group in match.groups())
            results[index] = value & 0xFFFFFFFF
    actual = [results[index] for index in range(1, len(expected) + 1)] if len(results) == len(expected) else []
    if actual != expected:
        raise SystemExit(f"opcode-0x0f nonfinite {args.engine} poll mismatch: {actual!r}")
    print(f"PASS: SHARC opcode-0x0f nonfinite seven-vector {args.engine} FIFO results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
