#!/usr/bin/env python3
"""Assemble Virtual-On's Model 2 polygon ROM in CPU-visible word order."""

from __future__ import annotations

import argparse
from pathlib import Path


def assemble_polygon_rom(rom_dir: Path) -> bytes:
    image = bytearray(0x1000000)
    for name, base in (
        ("mpr-18654.17", 0x000000),
        ("mpr-18655.21", 0x000002),
        ("mpr-18656.18", 0x800000),
        ("mpr-18657.22", 0x800002),
    ):
        data = (rom_dir / name).read_bytes()
        for index in range(0, len(data), 2):
            image[base + index * 2:base + index * 2 + 2] = data[index:index + 2]
    return bytes(image)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--output", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image = assemble_polygon_rom(args.rom_dir)
    args.output.write_bytes(image)
    print(f"wrote {len(image):#x} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
