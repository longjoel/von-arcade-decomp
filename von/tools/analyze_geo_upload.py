#!/usr/bin/env python3
"""Locate the captured geometry upload in the Model 2 main_data ROM region."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


ROM_SIZE = 0x400000
REGION_SIZE = 0x2000000
WORD_RE = re.compile(r"geo_prg_data: ([0-9a-fA-F]{4})")


def load_word_pair(target: bytearray, low: bytes, high: bytes, base: int) -> None:
    if len(low) != ROM_SIZE or len(high) != ROM_SIZE:
        raise ValueError("main_data ROMs must each be exactly 0x400000 bytes")
    for index in range(ROM_SIZE // 2):
        target[base + index * 4 : base + index * 4 + 2] = low[index * 2 : index * 2 + 2]
        target[base + index * 4 + 2 : base + index * 4 + 4] = high[index * 2 : index * 2 + 2]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, default=Path(__file__).parents[1] / "build/disasm/vonj-boot.trace")
    parser.add_argument("--rom-dir", type=Path, default=Path(__file__).parents[1] / "artifacts")
    args = parser.parse_args()

    words = [int(match, 16) for match in WORD_RE.findall(args.trace.read_text(encoding="ascii"))]
    if len(words) != 9340:
        raise SystemExit(f"expected 9340 geometry words, found {len(words)}")

    main_data = bytearray(REGION_SIZE)
    load_word_pair(
        main_data,
        (args.rom_dir / "mpr-18648.11").read_bytes(),
        (args.rom_dir / "mpr-18649.12").read_bytes(),
        0x000000,
    )
    load_word_pair(
        main_data,
        (args.rom_dir / "mpr-18650.9").read_bytes(),
        (args.rom_dir / "mpr-18651.10").read_bytes(),
        0x800000,
    )

    little = b"".join(word.to_bytes(2, "little") for word in words)
    big = b"".join(word.to_bytes(2, "big") for word in words)
    print(f"Captured {len(words)} words ({len(little)} bytes)")
    for label, stream in (("little-endian", little), ("big-endian", big)):
        offset = main_data.find(stream)
        if offset < 0:
            print(f"{label}: no exact match")
        else:
            print(f"{label}: main_data offset=0x{offset:08x}, bus address=0x{0x02000000 + offset:08x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
