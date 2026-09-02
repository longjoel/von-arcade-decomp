#!/usr/bin/env python3
"""Verify MAME's live SHARC signed-angle regression trace."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXPECTED = (
    "00000000", "3f7fffff", "3f350610", "3f3503d8",
    "3f800000", "b8492eef", "3f35019c", "bf35084a",
    "b3bbbd00", "bf7fffff", "38c92eef", "bf7fffff",
    "bf35019c", "bf35084a", "bf800000", "b8492eef",
)
OUTPUT = re.compile(
    r"vonj_sharc_output: pc=0203c[0-9a-f] address=00c00000 data=([0-9a-f]+)"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()
    actual = tuple(OUTPUT.findall(args.trace.read_text(encoding="utf-8", errors="replace")))
    if actual != EXPECTED:
        raise SystemExit(f"SHARC trig trace mismatch: got {actual!r}, expected {EXPECTED!r}")
    print("PASS: MAME SHARC signed-angle regression trace")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
