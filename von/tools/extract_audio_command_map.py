#!/usr/bin/env python3
"""Resolve the 68000 sound command table for the i960 command vocabulary.

The 68000 driver decodes a host packet `ae HH LL` in `0x6034b8`. If `HH` is
in `0x10..0x6f` it indexes a two-level table rooted at the pointer word
`[0x60801c]`:

    A4 = [0x60801c] + entry[HH-0x10]        (first-level table)
    A2 = [0x60801c] + entry2[LL]             (second-level offset)
    control = (A2)

`control == 0x00` selects the sequence path `0x603518`: a 3-byte prefix
then a 32-bit sequence pointer (into sample ROM) at `A2+3`. `control & 0x80`
selects the one-shot voice path `0x6035a0`, where the payload stream starts
at `A2+1` in program ROM.

This tool walks the whole table, annotates each command with the i960 asset
name from `von/sound-id-names.json` when available, and writes
`von/audio-command-map.json`.
"""

from __future__ import annotations

import argparse
import json
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGE = ROOT / "von/build/disasm/vonj-audio.bin"
DEFAULT_NAMES = ROOT / "von/sound-id-names.json"
POINTER_OFFSET = 0x801C  # [0x60801c]
COMMAND_TABLE_ADDR = 0x600000 + POINTER_OFFSET
HH_MIN = 0x10
HH_MAX = 0x6F
STREAM_PREVIEW = 16


def u16(data: bytes, offset: int) -> int:
    return struct.unpack_from(">H", data, offset)[0]


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from(">I", data, offset)[0]


def build_map(data: bytes, names: dict[str, str]) -> dict:
    pointer = u32(data, POINTER_OFFSET)
    base = pointer - 0x600000
    max_high = u16(data, base)
    first_level = []
    commands: dict[str, dict] = {}
    for index in range(max_high + 1):
        high = HH_MIN + index
        table = base + u16(data, base + 2 + index * 2)
        max_low = u16(data, table)
        first_level.append({
            "hh": high,
            "max_ll": max_low,
            "table": 0x600000 + table,
        })
        for low in range(max_low + 1):
            command = (high << 8) | low
            entry = base + u16(data, table + 2 + low * 2)
            control = data[entry]
            record: dict = {
                "entry": 0x600000 + entry,
                "control": control,
                "name": names.get(f"0x{command:04x}"),
            }
            if control == 0x00:
                # 0x603582 skips 3 prefix bytes, then loads a 32-bit
                # sequence pointer (into the sample region) and keeps the
                # rest of the record as a pointer list terminated by
                # 0xfffffff1.
                record["sequence_pointer"] = u32(data, entry + 3)
                record["record"] = data[entry:entry + 32].hex(" ")
            elif control & 0x80:
                # 0x6035a0: the inline stream begins at entry+1 with a
                # 3-byte sample packet `9a/9b/9c, index, param`, then a
                # wait byte and an `ff 2f` terminator.
                record["opcode"] = data[entry + 1]
                record["sample"] = data[entry + 2]
                record["param"] = data[entry + 3]
                record["stream"] = data[entry + 1:entry + 1 + STREAM_PREVIEW].hex(" ")
            else:
                record["payload"] = data[entry + 1:entry + 1 + STREAM_PREVIEW].hex(" ")
            commands[f"0x{command:04x}"] = record
    return {
        "schema": "von-audio-command-map/1",
        "pointer_offset": POINTER_OFFSET,
        "command_table": COMMAND_TABLE_ADDR,
        "pointer": pointer,
        "first_level": first_level,
        "command_count": len(commands),
        "commands": commands,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", nargs="?", type=Path, default=DEFAULT_IMAGE,
                        help="disassembled 68000 sound image")
    parser.add_argument("--names", type=Path, default=DEFAULT_NAMES)
    parser.add_argument("-o", "--output", type=Path,
                        default=ROOT / "von/audio-command-map.json")
    args = parser.parse_args()
    if not args.image.is_file():
        parser.error(f"missing image: {args.image} (run ./vonctl disasm audio)")
    names = {}
    if args.names.is_file():
        names = json.loads(args.names.read_text())["names"]
    report = build_map(args.image.read_bytes(), names)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({report['command_count']} commands)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
