#!/usr/bin/env python3
"""Decode Virtual-On ROM model part tables from main_data.

A model table is a flat run of [tpa, tha, oba] triples (texture params
plus polygon ROM address) interrupted by [0, 0, small] subgroup markers,
preceded by a header block and separated from the next table by zero
padding and 0xffffffff. Record layout verified triple-by-triple against
MAME trace object events: every sampled table triple matches the
(tpa, tha, oba) the game actually submits.

Reference table: main_data offset 0xbed828 (bus 0x02bed828), 19 part
records, header at 0xbed800, next table at 0xbed948.

A second layout (variant B) appears at 0xbed700: [tpa, oba, X] with
tpa-range 0x004axxxx, e.g. tpa=004a0fd2 for oba=0091c255 (trace shows
tha=tpa there). Its X field is undecoded: for oba=0091c02b the trace
tpa (004a0e20) equals the previous record's X, not its own
(004a1022). Some variant-B parts (009182dc) never submit in any
capture: inactive roster models.
"""
from __future__ import annotations

import argparse
import struct
from pathlib import Path


def load_main_data(rom_dir: Path) -> bytes:
    def load_word_pair(target: bytearray, low: bytes, high: bytes, base: int) -> None:
        for index in range(len(low) // 2):
            target[base + index * 4:base + index * 4 + 2] = low[index * 2:index * 2 + 2]
            target[base + index * 4 + 2:base + index * 4 + 4] = high[index * 2:index * 2 + 2]

    image = bytearray(0x2000000)
    load_word_pair(image,
                   (rom_dir / "mpr-18648.11").read_bytes(),
                   (rom_dir / "mpr-18649.12").read_bytes(), 0x000000)
    load_word_pair(image,
                   (rom_dir / "mpr-18650.9").read_bytes(),
                   (rom_dir / "mpr-18651.10").read_bytes(), 0x800000)
    return bytes(image)


def decode_records(words: list) -> list:
    """Split raw words into ('part', tpa, tha, oba) and ('marker', value)."""
    entries = []
    cursor = 0
    while cursor < len(words):
        if (cursor + 2 < len(words) and words[cursor] == 0
                and words[cursor + 1] == 0 and words[cursor + 2] <= 0xffff):
            entries.append(("marker", words[cursor + 2]))
            cursor += 3
        elif cursor + 2 < len(words):
            entries.append(("part", words[cursor], words[cursor + 1], words[cursor + 2]))
            cursor += 3
        else:
            entries.append(("truncated", words[cursor]))
            cursor += 1
    return entries


def decode_directory(words: list) -> list:
    """Split raw words into 6-word directory entries.

    Observed at maincpu 0xc9100 (10 entries): [range_end, range_start,
    struct_a, aux0, struct_b, aux1]. The 0xc9b50 walker strides the
    [tpa, tha, oba] records 12 bytes at a time from range_end, bounded
    by the struct count; a record whose oba word is <= 5 takes the
    filing body (parallel pose entry stored to dispatch slot 3*oba at
    0x562430), larger obas skip it via the unsigned-greater branch.
    """
    entries = []
    for cursor in range(0, len(words) // 6 * 6, 6):
        chunk = words[cursor:cursor + 6]
        entries.append({
            "range_end": chunk[0], "range_start": chunk[1],
            "struct_a": chunk[2], "aux0": chunk[3],
            "struct_b": chunk[4], "aux1": chunk[5],
        })
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rom-dir", type=Path, default=Path("von/artifacts"))
    parser.add_argument("--offset", type=lambda value: int(value, 0), required=True,
                        help="main_data offset of the first record word")
    parser.add_argument("--words", type=int, required=True)
    args = parser.parse_args()
    data = load_main_data(args.rom_dir)
    words = list(struct.unpack(f"<{args.words}I", data[args.offset:args.offset + args.words * 4]))
    for entry in decode_records(words):
        if entry[0] == "part":
            print(f"part tpa={entry[1]:08x} tha={entry[2]:08x} oba={entry[3]:08x}")
        elif entry[0] == "marker":
            print(f"marker value={entry[1]}")
        else:
            print(f"truncated word={entry[1]:08x}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
