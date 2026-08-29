#!/usr/bin/env python3
"""Reconstruct the linear Z80 cpu3 image from MAME's word-swapped ROM."""

from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_SIZE = 0x20000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=Path(__file__).parents[1] / "artifacts/epr-18643a.7")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    raw = args.rom.read_bytes()
    if len(raw) != IMAGE_SIZE:
        raise ValueError(f"expected {IMAGE_SIZE:#x} bytes, got {len(raw):#x}")
    image = bytearray(IMAGE_SIZE)
    for offset in range(0, IMAGE_SIZE, 2):
        image[offset] = raw[offset + 1]
        image[offset + 1] = raw[offset]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    print(f"Wrote {len(image):#x} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
