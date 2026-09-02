#!/usr/bin/env python3
"""Verify direct host-FIFO results from the opcode-0x0f parity probe."""

from __future__ import annotations

import re
import sys
from pathlib import Path


EXPECTED = [0x00000000, 0x00003FFF, 0x00001FFF, 0xFFFFC000,
            0x00007FFF, 0xFFFFE000, 0x00000000]
PATTERN = re.compile(r"response-poll=(\d+) vector-index=(\d+)")


def read_results(path: Path) -> list[int]:
    results: dict[int, int] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PATTERN.search(line)
        if match:
            value, index = (int(group) for group in match.groups())
            results[index] = value & 0xFFFFFFFF
    return [results[index] for index in range(1, len(EXPECTED) + 1)] if len(results) == len(EXPECTED) else []


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit(f"usage: {sys.argv[0]} POLL_LOG")
    path = Path(sys.argv[1])
    actual = read_results(path)
    if actual != EXPECTED:
        raise SystemExit(f"opcode-0x0f poll mismatch: {actual!r}")
    print("PASS: SHARC opcode-0x0f seven-vector FIFO results")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
