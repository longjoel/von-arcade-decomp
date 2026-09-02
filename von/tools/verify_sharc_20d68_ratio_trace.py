#!/usr/bin/env python3
"""Verify the finite-ratio branch partition of SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


# Each tuple is (helper input F0/F1, required path marker, R10 at the
# correction stage, F15 at the common return).  The values are raw SHARC
# words, preserving the ROM's rounding behavior.
EXPECTED = (
    (("3f800000", "40000000"), "020d89", "00000001", "3eed6338"),
    (("40000000", "3f800000"), "020d81", "00000003", "3f8db70d"),
    (("3f800000", "c0000000"), "020d89", "00000001", "402b6374"),
    (("c0000000", "3f800000"), "020d81", "00000003", "bf8db70d"),
    (("3f800000", "40800000"), "020d89", "00000000", "3e7adbb0"),
    (("40800000", "3f800000"), "020d81", "00000002", "3fa9b465"),
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    records = []
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        if "vonj_sharc_20d68:" in line:
            records.append(dict(re.findall(r"(pc|f0|f1|f15|r10)=([0-9a-f]+)", line)))
    starts = [i for i, record in enumerate(records) if record.get("pc") == "020d68"]
    if len(starts) < len(EXPECTED):
        raise SystemExit(f"trace contains {len(starts)} helper calls; expected {len(EXPECTED)}")

    for number, start in enumerate(starts[:len(EXPECTED)], 1):
        end = starts[number] if number < len(starts) else len(records)
        call = records[start:end]
        (expected_input, marker, expected_r10, expected_output) = EXPECTED[number - 1]
        if (call[0].get("f0"), call[0].get("f1")) != expected_input:
            raise SystemExit(f"ratio call {number} has unexpected helper input")
        if marker not in {record.get("pc") for record in call}:
            raise SystemExit(f"ratio call {number} missed branch marker {marker}")
        stage = next((record for record in call if record.get("pc") == "020dab"), None)
        if stage is None or stage.get("r10") != expected_r10:
            raise SystemExit(f"ratio call {number} has unexpected R10 correction count")
        result = next((record for record in call if record.get("pc") == "020db4"), None)
        if result is None or result.get("f15") != expected_output:
            raise SystemExit(f"ratio call {number} has unexpected rounded result")

    print("PASS: SHARC helper-0x20d68 finite-ratio branch runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
