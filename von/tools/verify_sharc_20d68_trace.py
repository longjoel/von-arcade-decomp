#!/usr/bin/env python3
"""Verify captured normal paths through SHARC helper 0x20d68."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


COEFFICIENTS = (
    "3e8930a3", "3fddb3d7", "39800000", "bf3853ae",
    "bfb854a8", "4098123c", "408a3f7e", "00000000",
    "3f060a92", "3fc90fdb", "3f860a92", "40490fdb",
)
EXPECTED_PCS = (
    "020d68", "020d69", "020d6a", "020d6b", "020d6c", "020d6d",
    "020d6e", "020d6f", "020d70", "020d71", "020d72", "020d73",
    "020d74", "020d75", "020d76", "020d77", "020d78", "020d79",
    "020d7a", "020d7b", "020d7c", "020d7d", "020d7e", "020d7f",
    "020d80", "020d89", "020d8a", "020d8b", "020d8c", "020d8d",
    "020d8e", "020d8f", "020d90", "020d91", "020d92", "020d93",
    "020d94", "020d95", "020d96", "020d97", "020d98", "020d99",
    "020d9a", "020d9b", "020d9c", "020d9d", "020d9e", "020d9f",
    "020da0", "020da1", "020da2", "020da3", "020da4", "020da5",
    "020da6", "020da7", "020da8", "020da9", "020daa", "020dab",
    "020dac", "020dad", "020dae", "020daf", "020db0", "020db1",
    "020db2", "020db3", "020db4",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument(
        "--signed",
        action="store_true",
        help="verify the signed-normal (-1,1) path and its late sign correction",
    )
    args = parser.parse_args()

    lines = [
        line for line in args.trace.read_text(encoding="utf-8", errors="replace").splitlines()
        if "vonj_sharc_20d68:" in line
    ]
    if not lines:
        raise SystemExit("trace contains no helper-0x20d68 records")

    records = []
    for line in lines:
        fields = dict(re.findall(r"(pc|f0|f1|f15|dm303[0-9a-f]+)=([0-9a-f]+)", line))
        records.append(fields)

    pcs = tuple(record["pc"] for record in records)
    if pcs[: len(EXPECTED_PCS)] != EXPECTED_PCS:
        raise SystemExit("helper-0x20d68 normal-path PC sequence changed")
    first = records[0]
    expected_input = ("bf800000", "3f800000") if args.signed else ("3f800000", "3f800000")
    if (first.get("f0"), first.get("f1")) != expected_input:
        label = "(-1,1)" if args.signed else "(1,1)"
        raise SystemExit(f"trace does not start with the {label} helper input")
    for index, expected in enumerate(COEFFICIENTS):
        if records[0].get(f"dm303{index:02x}") != expected:
            raise SystemExit(f"coefficient DM 0x303{index:02x} changed")
    magnitude = records[EXPECTED_PCS.index("020db0")]
    if magnitude.get("f15") != "3f490fda":
        raise SystemExit("helper path no longer produces the pi/4 magnitude")
    if args.signed:
        final = records[EXPECTED_PCS.index("020db4")]
        if final.get("f15") != "bf490fda":
            raise SystemExit("signed helper path no longer applies the late negative sign")

    label = "signed normal-path" if args.signed else "normal-path"
    print(f"PASS: SHARC helper-0x20d68 {label} runtime trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
