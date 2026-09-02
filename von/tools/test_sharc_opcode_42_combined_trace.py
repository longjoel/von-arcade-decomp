#!/usr/bin/env python3
"""Verify the recorded combined-angle state writes for SHARC opcode 0x42."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = [
    (0x30209, 0x38000000),
    (0x3020A, 0x38000000),
    (0x3020B, 0x38000000),
    (0x30200, 0xB8492EEF),
    (0x30203, 0x3F800000),
    (0x30201, 0xBF800000),
    (0x30204, 0xB8492EEF),
    (0x30202, 0x80000000),
    (0x30205, 0x00000000),
    (0x30200, 0x311E1ABC),
    (0x30206, 0x38492EEF),
    (0x30201, 0x38492EEF),
    (0x30207, 0x3F800000),
    (0x30202, 0x3F800000),
    (0x30208, 0xB8492EEF),
    (0x30203, 0xB8C92EEF),
    (0x30206, 0x3F800000),
    (0x30204, 0xBF800000),
    (0x30207, 0xB8C92EEF),
    (0x30205, 0x38492EEF),
    (0x30208, 0x311E1ABC),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    pattern = re.compile(
        r"vonj_sharc_opcode42_state: pc=[0-9a-f]+ "
        r"address=([0-9a-f]+) data=([0-9a-f]+)"
    )
    actual = []
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.search(line)
        if match:
            address, data = match.groups()
            actual.append((int(address, 16), int(data, 16)))
    if actual[-len(EXPECTED):] != EXPECTED:
        raise SystemExit(
            "combined opcode-0x42 state-write suffix does not match the recorded oracle"
        )
    print("PASS: SHARC opcode-0x42 combined-angle state-write trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
