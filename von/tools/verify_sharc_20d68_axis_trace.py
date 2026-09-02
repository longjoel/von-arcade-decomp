#!/usr/bin/env python3
"""Verify the zero-first-input early path through SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED_PCS = (
    "020d68", "020d69", "020d6a", "020d6b", "020d6c", "020d6d",
    "020d6e", "020d6f", "020d70", "020d71", "020d72", "020d73",
    "020db5", "020db6", "020db7", "020db0", "020db1", "020db2",
    "020db3", "020db4",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    records = []
    for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines():
        if "vonj_sharc_20d68:" in line:
            records.append(dict(re.findall(r"(pc|f0|f1|f15)=([0-9a-f]+)", line)))
    if not records:
        raise SystemExit("trace contains no helper-0x20d68 records")
    if tuple(record["pc"] for record in records)[:len(EXPECTED_PCS)] != EXPECTED_PCS:
        raise SystemExit("helper-0x20d68 zero-first-input path changed")
    if (records[0].get("f0"), records[0].get("f1")) != ("00000000", "3f800000"):
        raise SystemExit("trace does not start with the (0,1) helper input")
    final = records[len(EXPECTED_PCS) - 1]
    if (final.get("f0"), final.get("f15")) != ("00000000", "00000000"):
        raise SystemExit("zero-first-input path no longer returns zero")

    print("PASS: SHARC helper-0x20d68 zero-first-input runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
