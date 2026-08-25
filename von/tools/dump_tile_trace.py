#!/usr/bin/env python3
"""Render the latest 64-column tile-map state from a MAME tile trace."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TILE_RE = re.compile(
    r"tile_write: (?:pc=[0-9a-fA-F]+ )?offset=(?P<offset>[0-9a-fA-F]+) "
    r"data=(?P<data>[0-9a-fA-F]+) mask=(?P<mask>[0-9a-fA-F]+)"
)


def render(trace: Path, rows: int, columns: int) -> list[str]:
    tiles = [0] * (rows * columns)
    for line in trace.read_text(errors="replace").splitlines():
        match = TILE_RE.search(line)
        if not match:
            continue
        offset = int(match.group("offset"), 16)
        if offset >= len(tiles):
            continue
        data = int(match.group("data"), 16)
        mask = int(match.group("mask"), 16)
        tiles[offset] = (tiles[offset] & ~mask) | (data & mask)

    lines = []
    for row in range(rows):
        text = []
        for value in tiles[row * columns : (row + 1) * columns]:
            code = value & 0x00ff
            text.append(chr(code) if 0x20 <= code <= 0x7e else " ")
        lines.append("".join(text).rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--rows", type=int, default=64)
    parser.add_argument("--columns", type=int, default=64)
    args = parser.parse_args()

    output = "\n".join(render(args.trace, args.rows, args.columns)) + "\n"
    if args.output:
        args.output.write_text(output, encoding="ascii")
    else:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
