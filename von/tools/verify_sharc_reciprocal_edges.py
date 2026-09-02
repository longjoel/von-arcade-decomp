#!/usr/bin/env python3
"""Verify reciprocal-service edge results and optional DRC/interpreter parity."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = [
    0xFFFFFFFF, 0x00000000, 0x7F800000, 0xFFFFFFFF, 0xFFFFFFFF,
    0xFFFFFFFF, 0x00000001, 0xFFFFFFFF, 0xFFFFFFFF, 0xFFFFFFFF,
]
RESPONSE = re.compile(r"response=0x([0-9a-fA-F]{8})")


def read_results(path: Path) -> list[int]:
    return [int(match, 16) for match in RESPONSE.findall(path.read_text(encoding="utf-8"))]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("comparison_log", type=Path, nargs="?")
    args = parser.parse_args()

    actual = read_results(args.log)
    if actual != EXPECTED:
        raise SystemExit(f"reciprocal edge mismatch: {[hex(value) for value in actual]}")
    if args.comparison_log is not None:
        comparison = read_results(args.comparison_log)
        if comparison != actual:
            raise SystemExit("reciprocal edge DRC/interpreter parity mismatch")
    suffix = " with DRC/interpreter parity" if args.comparison_log is not None else ""
    print(f"PASS: SHARC reciprocal-service edge results{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
