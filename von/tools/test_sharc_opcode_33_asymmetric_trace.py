#!/usr/bin/env python3
"""Verify opcode 0x33's asymmetric two-pass writeback oracle."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = [
    (0x30200, 0x40DFFF9B), (0x30206, 0xBF800B01),
    (0x30201, 0x40FFFF37), (0x30207, 0xC0000649),
    (0x30202, 0x410FFF69), (0x30208, 0xC0400713),
    (0x30203, 0x3F8004B8), (0x30206, 0x40800065),
    (0x30204, 0x4000025B), (0x30207, 0x40A000C9),
    (0x30205, 0x4040025C), (0x30208, 0x40C0012E),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    pattern = re.compile(
        r"vonj_sharc_opcode33_state: pc=[0-9a-f]+ "
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
            "asymmetric opcode-0x33 state-write suffix does not match the recorded oracle"
        )
    print("PASS: SHARC opcode-0x33 asymmetric state-write trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
