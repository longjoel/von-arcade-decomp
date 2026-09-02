#!/usr/bin/env python3
"""Verify the 2-sqrt(3) threshold boundary of SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = (
    ("3e8930a2", 57, "020d97", "00000000", "3e860a91"),
    ("3e8930a3", 69, "020d8b", "00000001", "3e860a92"),
    ("3e8930a4", 69, "020d8b", "00000001", "3e860a93"),
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
        input_word, expected_length, marker, expected_r10, expected_output = EXPECTED[number - 1]
        if (call[0].get("f0"), call[0].get("f1")) != (input_word, "3f800000"):
            raise SystemExit(f"threshold call {number} has unexpected input")
        if len(call) != expected_length or marker not in {record.get("pc") for record in call}:
            raise SystemExit(f"threshold call {number} took an unexpected branch length")
        stage = next((record for record in call if record.get("pc") == "020dab"), None)
        if stage is None or stage.get("r10") != expected_r10:
            raise SystemExit(f"threshold call {number} has unexpected R10")
        result = next((record for record in call if record.get("pc") == "020db4"), None)
        if result is None or result.get("f15") != expected_output:
            raise SystemExit(f"threshold call {number} has unexpected rounded result")

    print("PASS: SHARC helper-0x20d68 threshold runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
