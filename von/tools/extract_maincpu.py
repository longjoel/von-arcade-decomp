#!/usr/bin/env python3
"""Reconstruct the little-endian i960 maincpu region from the four ROMs."""

from __future__ import annotations

import argparse
from pathlib import Path


ROM_SIZE = 0x80000
REGION_SIZE = 0x200000


def load_word_pair(target: bytearray, low: bytes, high: bytes, base: int) -> None:
    if len(low) != ROM_SIZE or len(high) != ROM_SIZE:
        raise ValueError("maincpu ROMs must each be exactly 0x80000 bytes")
    for index in range(ROM_SIZE // 2):
        target[base + index * 4 : base + index * 4 + 2] = low[index * 2 : index * 2 + 2]
        target[base + index * 4 + 2 : base + index * 4 + 4] = high[index * 2 : index * 2 + 2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    names = (
        ("epr-18664b.15", "epr-18665b.16", 0x000000),
        ("epr-18666.13", "epr-18667.14", 0x100000),
    )
    image = bytearray(REGION_SIZE)
    for low_name, high_name, base in names:
        low = (args.rom_dir / low_name).read_bytes()
        high = (args.rom_dir / high_name).read_bytes()
        load_word_pair(image, low, high, base)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    print(f"Wrote {len(image):#x} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
