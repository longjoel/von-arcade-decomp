#!/usr/bin/env python3
"""Verify a captured 0x28b80 geometry buffer against recovered semantics."""

from __future__ import annotations

import argparse
from pathlib import Path


def raw_logb(bits: int) -> int:
    bits &= 0x7FFFFFFF
    exponent = (bits >> 23) & 0xFF
    fraction = bits & 0x7FFFFF
    if exponent:
        return exponent - 127
    if not fraction:
        return -10000
    return fraction.bit_length() - 1 - 149


def conversion(raw_bits: int) -> int:
    result = raw_logb(raw_bits) + 128
    return max(0, min(0x80, result))


def expected() -> list[int]:
    result = []
    value = 0
    for _ in range(0x2000):
        word = 0
        for shift in (0, 8, 16, 24):
            word |= conversion(value) << shift
            value = (value + 0x7F00) & 0xFFFFFFFF
        result.append(word)
    return result


def load_dump(path: Path) -> list[int]:
    values = []
    for line in path.read_text().splitlines():
        if not line or line.startswith("#"):
            continue
        _, value = line.split()
        values.append(int(value, 16))
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dump", type=Path)
    args = parser.parse_args()
    actual = load_dump(args.dump)
    wanted = expected()
    if actual == wanted:
        print(f"match: {len(actual)} words")
        return 0
    for index, (got, want) in enumerate(zip(actual, wanted)):
        if got != want:
            print(f"mismatch at 0x{index:04x}: got {got:08x}, expected {want:08x}")
            return 1
    print(f"length mismatch: got {len(actual)}, expected {len(wanted)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
