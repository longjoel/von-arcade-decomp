#!/usr/bin/env python3
"""Decode the three-byte command packets in the 68000 sound ROM streams.

The routine at sound-CPU address $603dbc dispatches on the command byte's
high nibble.  The normal packet handlers consume the command byte and two
payload bytes, then leave the next packet address in the stream state.  This
tool exposes those packets without pretending their fields are already
identified as notes, instruments, or durations.
"""

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
    return int.from_bytes(data[offset:offset + 2], "big")


def dispatch_stream(data: bytes, base: int, event_id: int,
                    maximum_packets: int) -> dict:
    offset = u16(data, base + 2 + event_id * 2)
    if offset == 0xffff:
        return {"id": event_id, "status": "empty"}
    start = base + offset
    packets = []
    cursor = start
    for index in range(maximum_packets):
        if cursor + 3 > len(data):
            break
        raw = data[cursor:cursor + 3]
        command = raw[0]
        packets.append({"index": index, "offset": cursor,
                        "command": command,
                        "payload": [raw[1], raw[2]],
                        "raw": raw.hex(" ")})
        cursor += 3
        # FF is used by the command language for control/termination paths;
        # retain it in the report but avoid walking arbitrary ROM padding.
        if command == 0xff and raw[1:] == b"\xff\xff":
            break
    return {"id": event_id, "start": start,
            "cpu_address": start + 0x600000,
            "packets": packets,
            "bytes_consumed": cursor - start}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rom", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    parser.add_argument("--table-offset", type=lambda value: int(value, 0), default=0x8008,
                        help="ROM offset containing the sequence-table pointer")
    parser.add_argument("--maximum-packets", type=int, default=4096)
    args = parser.parse_args()
    if args.maximum_packets <= 0:
        parser.error("--maximum-packets must be positive")
    data = word_swap(args.rom.read_bytes())
    pointer = int.from_bytes(data[args.table_offset:args.table_offset + 4], "big")
    if not 0x600000 <= pointer < 0x700000:
        raise ValueError(f"invalid sequence-table pointer: {pointer:#x}")
    base = pointer - 0x600000
    maximum = u16(data, base)
    streams = []
    for event_id in range(0, maximum + 1):
        stream = dispatch_stream(data, base, event_id, args.maximum_packets)
        if stream.get("status") != "empty":
            streams.append(stream)
    report = {"rom": str(args.rom), "packet_bytes": 3,
              "dispatch_table_offset": base, "maximum_event_id": maximum,
              "populated_stream_count": len(streams), "streams": streams}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({len(streams)} streams)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
