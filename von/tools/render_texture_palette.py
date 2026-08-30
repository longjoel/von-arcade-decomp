#!/usr/bin/env python3
"""Render decoded texture bytes through a captured Model 2 palette state.

Timestamped traces can be filtered with ``--time`` so a later palette rewrite
does not affect an earlier scene.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EVENT_TIME = re.compile(r"(?:^| )time=([0-9.e+-]+)(?: |$)")


def parse_trace(path: Path, at_time: float | None = None) -> tuple[dict[int, int], dict[int, int], dict[int, int]]:
    palette: dict[int, int] = {}
    colorxlat: dict[int, int] = {}
    luma: dict[int, int] = {}
    for line in path.read_text().splitlines():
        event_time = EVENT_TIME.search(line)
        if at_time is not None and event_time and float(event_time[1]) > at_time:
            continue
        match = re.search(r"vonj_palette_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+).*value=([0-9a-f]+)", line)
        if match:
            palette[int(match[1], 16)] = int(match[2], 16)
        match = re.search(r"vonj_colorxlat_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+).*value=([0-9a-f]+)", line)
        if match:
            colorxlat[int(match[1], 16)] = int(match[2], 16)
        match = re.search(r"vonj_luma_write: (?:time=[0-9.e+-]+ )?offset=([0-9a-f]+) data=([0-9a-f]+)", line)
        if match:
            luma[int(match[1], 16)] = int(match[2], 16)
    return palette, colorxlat, luma


def gamma(value: int) -> int:
    return max((value - 64) * 255 // 191, 0)


def palette_rgb(index: int, colorbase: int, palette: dict[int, int],
                colorxlat: dict[int, int], luma: dict[int, int]) -> tuple[int, int, int]:
    """Map one 4bpp texel through the captured palette pipeline."""
    color = palette.get(0x1000 + colorbase, 0) & 0x7fff
    red = (color >> 0) & 0x1f
    green = (color >> 5) & 0x1f
    blue = (color >> 10) & 0x1f
    level = luma.get(index * 8, 0)
    return (
        gamma(colorxlat.get((red << 8) + level, 0) & 0xff),
        gamma(colorxlat.get(0x2000 + (green << 8) + level, 0) & 0xff),
        gamma(colorxlat.get(0x4000 + (blue << 8) + level, 0) & 0xff),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bank", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/bank0-primary.bin"))
    parser.add_argument("--trace", type=Path,
                        default=Path("von/build/disasm/vonj-palette-luma.trace"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/texture-pipeline/color"))
    parser.add_argument("--bases", default="0,1,2,4,7,16,22,25")
    parser.add_argument("--time", type=float,
                        help="use palette state at or before this emulated timestamp")
    args = parser.parse_args()

    palette, colorxlat, luma = parse_trace(args.trace, args.time)
    packed = args.bank.read_bytes()
    pixels = bytearray()
    for y in range(1024):
        for x in range(2048):
            x2 = x
            y2 = y
            offset = (y2 // 2) * 512 + (x2 // 2)
            word = int.from_bytes(packed[(offset >> 1) * 4:(offset >> 1) * 4 + 4], "little")
            if offset & 1:
                word >>= 16
            if (y & 1) == 0:
                word >>= 8
            if (x & 1) == 0:
                word >>= 4
            pixels.append((word & 0x0f) << 4)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    for base_text in args.bases.split(","):
        base = int(base_text, 0)
        output = bytearray()
        for index in pixels:
            output.extend(palette_rgb(index >> 4, base, palette, colorxlat, luma))
        path = args.output_dir / f"bank0-colorbase-{base:03d}.ppm"
        path.write_bytes(b"P6\n2048 1024\n255\n" + output)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
