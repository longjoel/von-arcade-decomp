#!/usr/bin/env python3
"""Verify architectural ASTAT/STKY samples from the nonfinite FIFO probe."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SAMPLE = re.compile(
    r"response-poll=.*?vector-index=(\d+) .*?astat=0x([0-9a-fA-F]+) stky=0x([0-9a-fA-F]+)"
)
AIS = 0x20


def samples(path: Path) -> list[tuple[int, int, int]]:
    found = []
    for line in path.read_text(encoding="utf-8").splitlines():
        match = SAMPLE.search(line)
        if match:
            found.append((int(match.group(1)), int(match.group(2), 16), int(match.group(3), 16)))
    return found


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", type=Path)
    parser.add_argument("--engine", choices=("interpreter", "drc"), required=True)
    parser.add_argument("comparison_log", type=Path, nargs="?")
    args = parser.parse_args()
    found = samples(args.log)
    if [item[0] for item in found] != list(range(1, 9)):
        raise SystemExit(f"expected eight ordered state samples, got {[item[0] for item in found]}")
    if any((stky & AIS) == 0 for _, _, stky in found):
        raise SystemExit(f"{args.engine} state samples never set STKY.AIS")
    if args.comparison_log is not None:
        comparison = samples(args.comparison_log)
        if comparison != found:
            raise SystemExit(f"{args.engine} ASTAT/STKY samples differ from comparison log")
    print(f"PASS: SHARC opcode-0x0f {args.engine} architectural state samples set STKY.AIS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
