#!/usr/bin/env python3
"""Verify the captured non-normal input behavior of helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


# (normalized helper F0/F1, required path marker, helper result, caller output,
#  final low ASTAT flags; upper ASTAT state is retained across calls)
EXPECTED = (
    (("ffffffff", "3f800000"), "020d9a", "ffffffff", "80000000", 0x620),
    (("3f800000", "ffffffff"), "020d9a", "ffffffff", "80000000", 0x620),
    (("7f7fffff", "3f800000"), "020db8", "3fc90fdb", "00003fff", 0x600),
    (("3f800000", "7f7fffff"), "020db5", "00000000", "00000000", 0x400),
    (("00000000", "3f800000"), "020db5", "00000000", "00000000", 0x401),
    (("3f800000", "00000000"), "020dbb", "3fc90fdb", "00003fff", 0x400),
    (("ff7fffff", "3f800000"), "020db8", "bfc90fdb", "ffffc000", 0x404),
    (("3f800000", "ffffffff"), "020d9a", "ffffffff", "80000000", 0x620),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    lines = args.trace.read_text(encoding="utf-8", errors="replace").splitlines()
    starts = [
        i for i, line in enumerate(lines)
        if "vonj_sharc_20d68:" in line and "pc=020d68 " in line
    ]
    if len(starts) < len(EXPECTED):
        raise SystemExit(f"trace contains {len(starts)} helper calls; expected {len(EXPECTED)}")

    for number, start in enumerate(starts[:len(EXPECTED)], 1):
        end = starts[number] if number < len(starts) else len(lines)
        chunk = lines[start:end]
        records = [
            dict(re.findall(r"(pc|astat|f0|f1|f15)=([0-9a-f]+)", line))
            for line in chunk if "vonj_sharc_20d68:" in line
        ]
        expected_input, marker, expected_result, expected_output, expected_astat = EXPECTED[number - 1]
        if (records[0].get("f0"), records[0].get("f1")) != expected_input:
            raise SystemExit(f"non-normal call {number} has unexpected normalized input")
        if marker not in {record.get("pc") for record in records}:
            raise SystemExit(f"non-normal call {number} missed path marker {marker}")
        result = next((record for record in records if record.get("pc") == "020db4"), None)
        if result is None or result.get("f15") != expected_result:
            raise SystemExit(f"non-normal call {number} has unexpected helper result")
        if int(result.get("astat", "-1"), 16) & 0x7ff != expected_astat:
            raise SystemExit(f"non-normal call {number} has unexpected low ASTAT flags")
        output = next(
            (re.search(r"data=([0-9a-f]+)", line).group(1)
             for line in chunk if "vonj_sharc_output:" in line and "address=00c00000" in line),
            None,
        )
        if output != expected_output:
            raise SystemExit(f"non-normal call {number} has unexpected caller output")

    print("PASS: SHARC helper-0x20d68 non-normal runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
