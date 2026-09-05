#!/usr/bin/env python3
"""Validate the common geometry-object packet prefix in a MAME trace."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EVENT = re.compile(r"vonj_geometry_object_fifo: pc=([0-9a-fA-F]+) data=([0-9a-fA-F]+)")
EXPECTED = (0x2F, 0xB6D0, 0x4C4C, 0xBB8B, 0x16, 0x6C, 0x15, 0x17, 0x14, 0xFFFFFF80)


def find_prefix(trace: Path) -> tuple[int, list[tuple[int, int]] | None]:
    events = []
    for line in trace.read_text().splitlines():
        match = EVENT.search(line)
        if match:
            events.append((int(match[1], 16), int(match[2], 16)))
    for start in range(0, len(events) - len(EXPECTED) + 1):
        data = tuple(value for _, value in events[start : start + len(EXPECTED)])
        if data == EXPECTED:
            return len(events), events[start : start + len(EXPECTED)]
    return len(events), None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    args = parser.parse_args()
    count, prefix = find_prefix(args.trace)
    if prefix is None:
        print(f"geometry packet prefix: not found ({count} FIFO events)")
        return 1
    pcs = ",".join(f"0x{pc:05x}" for pc, _ in prefix)
    print(f"geometry packet prefix: found ({count} FIFO events; PCs {pcs})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
