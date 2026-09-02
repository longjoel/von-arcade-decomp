#!/usr/bin/env python3
"""Verify the live six-vector opcode-0x45 spherical projection sweep."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = (
    (0x00000000, 0x3F7FFFFE, 0x80000000),
    (0x40000000, 0xB8C92EEE, 0x00000000),
    (0x00000000, 0xB8C92EEE, 0xBFFFFFFF),
    (0x3FB50610, 0x3F7FFCDF, 0xBF800001),
    (0xBF87C48C, 0x3F3FFDA7, 0xBF400002),
    (0x3F87C48C, 0x3F3FFDA7, 0x3F400002),
)
OUTPUT_PCS = (0x20BC6, 0x20BC9, 0x20BCD)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("probe_log", type=Path)
    args = parser.parse_args()

    requests = [
        line for line in args.probe_log.read_text(encoding="utf-8").splitlines()
        if re.search(r"probe: index=\d+", line)
    ]
    if len(requests) != len(EXPECTED):
        raise SystemExit(f"expected {len(EXPECTED)} probe requests, found {len(requests)}")

    outputs = []
    pattern = re.compile(r"vonj_sharc_output: pc=([0-9a-f]+).*data=([0-9a-f]+)")
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        match = pattern.search(line)
        if match and int(match.group(1), 16) in OUTPUT_PCS:
            outputs.append(int(match.group(2), 16))
    if len(outputs) != len(EXPECTED) * len(OUTPUT_PCS):
        raise SystemExit(f"expected {len(EXPECTED) * len(OUTPUT_PCS)} outputs, found {len(outputs)}")

    for index, wanted in enumerate(EXPECTED):
        actual = tuple(outputs[index * 3:index * 3 + 3])
        if actual != wanted:
            raise SystemExit(f"vector {index + 1} was {actual!r}, expected {wanted!r}")

    print("PASS: SHARC opcode-0x45 spherical projection sweep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
