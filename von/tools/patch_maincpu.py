#!/usr/bin/env python3
"""Binary-patch the i960 maincpu ROMs, mapping addresses to chip offsets.

The i960 region is built by interleaving two 0x80000 ROMs per 1 MiB half
(von/tools/extract_maincpu.py):

    0x000000..0x0fffff  epr-18664b.15 (low) + epr-18665b.16 (high)
    0x100000..0x1fffff  epr-18666.13  (low) + epr-18667.14  (high)

Within a half, every 4 image bytes are a word pair: bytes 0-1 low, 2-3 high.
This tool copies a ROM directory and applies (address, hex-bytes) patches in
place so MAME can boot the modified set (CRC warnings are expected).

  patch_maincpu.py --src <rom-dir> --dst <copy-dir> 0x1f370=4841434b
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

HALVES = [
    (0x000000, "epr-18664b.15", "epr-18665b.16"),
    (0x100000, "epr-18666.13", "epr-18667.14"),
]


def split(addr: int):
    for base, low, high in HALVES:
        if base <= addr < base + 0x100000:
            index = addr - base
            word, byte = divmod(index, 4)
            if byte < 2:
                return low, word * 2 + byte
            return high, word * 2 + (byte - 2)
    raise ValueError(f"address {addr:#x} outside the i960 maincpu region")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--src", type=Path, required=True)
    parser.add_argument("--dst", type=Path, required=True)
    parser.add_argument("patches", nargs="+", help="address=hexbytes, e.g. 0x1f370=4841434b")
    args = parser.parse_args()

    if args.dst.exists():
        shutil.rmtree(args.dst)
    shutil.copytree(args.src, args.dst, symlinks=False, dirs_exist_ok=True)

    for spec in args.patches:
        addr_text, _, hex_text = spec.partition("=")
        addr = int(addr_text, 0)
        data = bytes.fromhex(hex_text)
        # Each image byte maps to its own chip offset (the low/high interleave
        # alternates every two bytes), so patch byte by byte.
        blobs: dict[str, bytearray] = {}
        for i, value in enumerate(data):
            name, offset = split(addr + i)
            blob = blobs.get(name)
            if blob is None:
                blob = bytearray((args.dst / name).read_bytes())
                blobs[name] = blob
            blob[offset] = value
        for name, blob in blobs.items():
            (args.dst / name).write_bytes(blob)
        print(f"{addr:#08x}: {data.hex()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
