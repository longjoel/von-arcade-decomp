#!/usr/bin/env python3
"""Verify large finite exponent-distance cases of SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = (
    (("41800000", "3f800000"), "020d81", "00000002", "3fc11284"),
    (("3f800000", "41800000"), "020d89", "00000000", "3d7faade"),
    (("42800000", "3f800000"), "020d81", "00000002", "3fc70fe6"),
    (("3f800000", "42800000"), "020d89", "00000000", "3c7ffaab"),
    (("43800000", "3f800000"), "020d81", "00000002", "3fc88fdb"),
    (("3f800000", "43800000"), "020d89", "00000000", "3b7fffab"),
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
        expected_input, marker, expected_r10, expected_output = EXPECTED[number - 1]
        if (call[0].get("f0"), call[0].get("f1")) != expected_input:
            raise SystemExit(f"exponent-edge call {number} has unexpected input")
        if marker not in {record.get("pc") for record in call}:
            raise SystemExit(f"exponent-edge call {number} missed {marker}")
        stage = next((record for record in call if record.get("pc") == "020dab"), None)
        if stage is None or stage.get("r10") != expected_r10:
            raise SystemExit(f"exponent-edge call {number} has unexpected R10")
        result = next((record for record in call if record.get("pc") == "020db4"), None)
        if result is None or result.get("f15") != expected_output:
            raise SystemExit(f"exponent-edge call {number} has unexpected result")
        if "020d9a" not in {record.get("pc") for record in call}:
            raise SystemExit(f"exponent-edge call {number} skipped polynomial body")

    print("PASS: SHARC helper-0x20d68 exponent-edge runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
