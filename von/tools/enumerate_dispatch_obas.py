#!/usr/bin/env python3
"""Enumerate the 0x2be52b0 dispatch-table objects without MAME.

The i960 routines 0x90c10/0x90d50/0x90e80 index this 30-entry ROM
table by g0 % 30 and submit entry[2] through the geometry control
registers (see recovered_geometry_fifo_dispatch_90c10.c). Every
entry[2] carries bit 0x00800000, selecting polygon ROM with the low
22 bits as a word offset, so the table statically enumerates 30
polygon objects that trace sampling may never observe.

This tool reads the table straight from the ROM files through the
documented main_data layout (no MAME, no trace) and dumps each
object's window from the geometry ROM image alongside a manifest.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from decode_model_part_table import load_main_data


TABLE_ADDRESS = 0x2BE52B0
MAIN_DATA_BASE = 0x02000000
ENTRY_COUNT = 30
ENTRY_STRIDE = 12
POLYGON_ROM_BIT = 0x00800000
POLYGON_INDEX_MASK = 0x3FFFFF


def read_table(main_data: bytes, address: int = TABLE_ADDRESS,
               count: int = ENTRY_COUNT) -> list[tuple[int, int, int]]:
    offset = address - MAIN_DATA_BASE
    entries = []
    for index in range(count):
        word0, word1, word2 = struct.unpack_from(
            "<3I", main_data, offset + index * ENTRY_STRIDE)
        entries.append((word0, word1, word2))
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--geometry-rom", type=Path,
                        default=Path("von/build/disasm/geometry-rom.bin"))
    parser.add_argument("--output-dir", type=Path,
                        default=Path("von/build/disasm/dispatch-objects"))
    parser.add_argument("--window", type=int, default=0x1000)
    args = parser.parse_args()

    main_data = load_main_data(args.rom_dir)
    geometry = args.geometry_rom.read_bytes()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = []
    for index, (word0, word1, oba) in enumerate(read_table(main_data)):
        record = {"index": index, "ptr": f"{word0:08x}",
                  "ptr_copy": f"{word1:08x}", "oba": f"{oba:08x}",
                  "polygon_rom": bool(oba & POLYGON_ROM_BIT), "words": 0,
                  "file": None}
        if record["polygon_rom"]:
            start = (oba & POLYGON_INDEX_MASK) * 4
            end = min(start + args.window * 4, len(geometry))
            words = [int.from_bytes(geometry[pos:pos + 4], "little")
                     for pos in range(start, end, 4)]
            name = f"{index:02d}-oba{oba:08x}.hex"
            (args.output_dir / name).write_text(
                "\n".join(f"{value:08x}" for value in words) + "\n")
            record["words"] = len(words)
            record["file"] = name
        manifest.append(record)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n")
    polygon = sum(1 for record in manifest if record["polygon_rom"])
    print(f"Enumerated {len(manifest)} entries, {polygon} polygon-ROM "
          f"objects -> {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
