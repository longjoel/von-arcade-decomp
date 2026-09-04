#!/usr/bin/env python3
"""Report the 68000 sound-program sequence dispatch table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def word_swap(data: bytes) -> bytes:
    if len(data) % 2:
        raise ValueError("sound ROM must contain an even number of bytes")
    return b"".join(data[i + 1:i + 2] + data[i:i + 1]
                    for i in range(0, len(data), 2))


def u16(data: bytes, offset: int) -> int:
    if offset < 0 or offset + 2 > len(data):
        raise ValueError(f"word offset outside ROM: {offset:#x}")
    return int.from_bytes(data[offset:offset + 2], "big")


def relative_table(data: bytes, base: int, maximum: int) -> list[dict]:
    entries = []
    for index in range(maximum + 1):
        offset = u16(data, base + 2 + index * 2)
        target = base + offset
        entry = {"id": index, "offset": offset}
        if target >= len(data):
            entry["error"] = "target outside ROM"
        else:
            entry.update(target=target, cpu_address=target + 0x600000,
                         preview=data[target:target + 16].hex(" "))
        entries.append(entry)
    return entries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path, help="epr-18670.31 sound CPU ROM")
    parser.add_argument("-o", "--output", type=Path)
    parser.add_argument("--no-word-swap", action="store_true")
    parser.add_argument("--table-offset", type=lambda value: int(value, 0), default=0x8008,
                        help="ROM offset containing the table pointer")
    args = parser.parse_args()
    physical = args.rom.read_bytes()
    data = physical if args.no_word_swap else word_swap(physical)
    pointer = int.from_bytes(data[args.table_offset:args.table_offset + 4], "big")
    if not 0x600000 <= pointer < 0x700000:
        raise ValueError(f"invalid sound-ROM pointer: {pointer:#x}")
    base = pointer - 0x600000
    maximum = u16(data, base)
    streams = []
    for event_id in range(0, maximum + 1):
        offset = u16(data, base + 2 + event_id * 2)
        if offset == 0xffff:
            continue
        target = base + offset
        entry = {"id": event_id, "offset": offset}
        if target >= len(data):
            entry["error"] = "target outside ROM"
        else:
            entry.update(target=target, cpu_address=target + 0x600000,
                         preview=data[target:target + 16].hex(" "))
        streams.append(entry)
    # The first sound-command table contains a pointer to a second, larger
    # sequence/voice table.  Resolve it from the low word exactly as the
    # 68000 code does at $6027f0.
    voice_pointer = int.from_bytes(data[0x8004:0x8008], "big")
    if not 0x600000 <= voice_pointer < 0x700000:
        raise ValueError(f"invalid voice-table pointer: {voice_pointer:#x}")
    voice_base = voice_pointer - 0x600000
    voice_maximum = u16(data, voice_base)
    report = {
        "rom": str(args.rom),
        "logical_byte_order": "68000 big-endian after per-word swap",
        "dispatch_table": {"cpu_address": base + 0x600000,
                            "rom_offset": base,
                            "maximum_event_id": maximum,
                            "entry_stride": 2},
        "streams": streams,
        "voice_sequence_table": {
            "pointer_word_offset": 0x8004,
            "rom_offset": voice_base,
            "cpu_address": voice_base + 0x600000,
            "maximum_id": voice_maximum,
            "entries": relative_table(data, voice_base, voice_maximum),
        },
        "notes": [
            "Offsets are relative to the dispatch-table address.",
            "The sound program consumes streams through its 68000 event tick.",
            "Names and exact sample boundaries remain unresolved until SCSP voice descriptors are mapped.",
        ],
    }
    encoded = json.dumps(report, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded)
        print(f"wrote {args.output} ({len(streams)} populated streams)")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
