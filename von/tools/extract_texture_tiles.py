#!/usr/bin/env python3
"""Extract individual 4bpp texture tiles referenced by a MAME trace."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


COMMAND = re.compile(
    r"vonj_texture_command: (?:time=[0-9.e+-]+ )?uv=([0-9a-f]+) header=([0-9a-f]+) "
    r"tex=([0-9a-f]+),([0-9a-f]+),([0-9a-f]+),([0-9a-f]+) "
    r"attr=([0-9a-f]+) colorbase=([0-9a-f]+) sheet=(\d+) "
    r"size=(\d+)x(\d+) origin=(\d+),(\d+)"
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path,
                        default=Path("von/build/disasm/vonj-gameplay-texture.trace"))
    parser.add_argument("--bank", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/tiles"))
    parser.add_argument("--limit", type=int, default=128)
    args = parser.parse_args()

    packed = args.bank.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    seen: set[tuple[int, int, int, int, int]] = set()
    rows: list[tuple[str, int, int, int, int, int]] = []

    def texel(x: int, y: int) -> int:
        offset = (y // 2) * 512 + (x // 2)
        word = int.from_bytes(packed[(offset >> 1) * 4:(offset >> 1) * 4 + 4], "little")
        if offset & 1:
            word >>= 16
        if not (y & 1):
            word >>= 8
        if not (x & 1):
            word >>= 4
        return (word & 0x0f) * 17

    for match in COMMAND.finditer(args.trace.read_text()):
        groups = match.groups()
        header = int(groups[1], 16)
        colorbase = int(groups[7], 16)
        sheet = int(groups[8])
        width, height, origin_x, origin_y = map(int, groups[9:13])
        key = (header, width, height, origin_x, origin_y)
        if sheet or key in seen or width > 256 or height > 256:
            continue
        seen.add(key)
        x0 = (origin_x - 2048) & 2047
        y0 = (origin_y - 1024) & 1023
        pixels = bytearray(
            texel((x0 + x) & 2047, (y0 + y) & 1023)
            for y in range(height) for x in range(width)
        )
        name = f"{len(rows):03d}-cb{colorbase:03x}-{width}x{height}-at{x0:04x}_{y0:03x}.pgm"
        (args.output_dir / name).write_bytes(
            f"P5\n{width} {height}\n255\n".encode() + pixels)
        rows.append((name, colorbase, width, height, x0, y0))
        if len(rows) >= args.limit:
            break

    (args.output_dir / "index.tsv").write_text(
        "file\tcolorbase\twidth\theight\tx\ty\n" +
        "\n".join("\t".join(map(str, row)) for row in rows) + "\n")
    print(f"extracted {len(rows)} texture tiles to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
