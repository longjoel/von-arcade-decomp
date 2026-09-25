#!/usr/bin/env python3
"""Reconstruct the 68000 sound-CPU image from `epr-18670.31`.

MAME declares the 512 KiB sound program as `ROM_LOAD16_WORD_SWAP` for the
`audiocpu` region mapped at `0x600000-0x67ffff`, so each 16-bit word of the
dump is byte-swapped when the 68000 reads it. The reset vector in the
CPU-visible image is SSP `0x00005000` / PC `0x00601200`.

The EPROM is a single 8-bit part, so the transform is a pure per-word byte
swap. This tool validates the resulting reset vector before writing.
"""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


IMAGE_SIZE = 0x80000
LOAD_BASE = 0x600000
RESET_SP = 0x00005000
RESET_PC = 0x00601200


def word_swap(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("sound ROM must contain an even number of bytes")
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom", type=Path,
                        default=Path(__file__).parents[1] /
                        "artifacts/epr-18670.31")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    physical = args.rom.read_bytes()
    if len(physical) != IMAGE_SIZE:
        raise ValueError(f"expected {IMAGE_SIZE:#x} bytes, got {len(physical):#x}")
    image = word_swap(physical)
    sp, pc = struct.unpack_from(">II", image, 0)
    if sp != RESET_SP or pc != RESET_PC:
        raise ValueError(
            f"unexpected reset vector SSP={sp:#010x} PC={pc:#010x}; "
            "check the word-swap convention")
    if not LOAD_BASE <= pc < LOAD_BASE + IMAGE_SIZE:
        raise ValueError(f"reset PC {pc:#010x} outside audiocpu region")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(image)
    print(f"Wrote {len(image):#x} bytes to {args.output} "
          f"(reset SSP={sp:#x} PC={pc:#x})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
