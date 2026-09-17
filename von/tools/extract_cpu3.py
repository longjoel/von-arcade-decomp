#!/usr/bin/env python3
"""Reconstruct the linear Z80 cpu3 image from the communication EPROM.

`epr-18643a.7` is a single 8-bit 27C1001, so the dump is already in Z80 byte
order (reset vector `c3 a2 01` -> `jp $01A2`, then `di`/`im 2`/`ld sp,$A000`).
MAME declares it `ROM_LOAD16_WORD_SWAP` but never executes it (`m2comm`
simulates the board), so that declaration must not be treated as a byte-order
transform for analysis.
"""

from __future__ import annotations

import argparse
from pathlib import Path


IMAGE_SIZE = 0x20000


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path, default=Path(__file__).parents[1] / "artifacts/epr-18643a.7")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    image = args.rom.read_bytes()
    if len(image) != IMAGE_SIZE:
        raise ValueError(f"expected {IMAGE_SIZE:#x} bytes, got {len(image):#x}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    print(f"Wrote {len(image):#x} bytes to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
