#!/usr/bin/env python3
"""Verify the signed LOGB exponent-distance limits of SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


# (helper F0/F1, trace length, terminal marker, rounded F15 at 0x20db4)
EXPECTED = (
    (("4f800000", "3f800000"), 48, "020d81", "3fc90fdb"),
    (("3f800000", "4f800000"), 40, "020d89", "2f800000"),
    (("5f800000", "3f800000"), 48, "020d81", "3fc90fdb"),
    (("3f800000", "5f800000"), 40, "020d89", "1f800000"),
    (("7e800000", "3f800000"), 15, "020db8", "3fc90fdb"),
    (("3f800000", "7e800000"), 20, "020db5", "00000000"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    records = []
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        if "vonj_sharc_20d68:" in line:
            records.append(dict(re.findall(r"(pc|f0|f1|f15)=([0-9a-f]+)", line)))
    starts = [i for i, record in enumerate(records) if record.get("pc") == "020d68"]
    if len(starts) < len(EXPECTED):
        raise SystemExit(f"trace contains {len(starts)} helper calls; expected {len(EXPECTED)}")

    for number, start in enumerate(starts[:len(EXPECTED)], 1):
        end = starts[number] if number < len(starts) else len(records)
        call = records[start:end]
        expected_input, expected_length, marker, expected_output = EXPECTED[number - 1]
        if (call[0].get("f0"), call[0].get("f1")) != expected_input:
            raise SystemExit(f"LOGB-limit call {number} has unexpected input")
        if len(call) != expected_length or marker not in {record.get("pc") for record in call}:
            raise SystemExit(f"LOGB-limit call {number} took an unexpected path")
        result = next((record for record in call if record.get("pc") == "020db4"), None)
        if result is None or result.get("f15") != expected_output:
            raise SystemExit(f"LOGB-limit call {number} has unexpected rounded result")

    print("PASS: SHARC helper-0x20d68 LOGB-limit runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
