#!/usr/bin/env python3
"""Extract per-stage intro audio packet scripts from an audio-queue tap log.

Reads a replay_input_health.lua log captured with a write tap over the
i960 audio ring (0x0051aa70-0x0051aabf) and prints the ordered datum
packets per stage window as JSON: {stage_index: [{offset, bytes}]} with
offsets relative to the given spawn frame.

Grouping rules (documented so the table stays regenerable): stores from
producer PC 0x2a4cc are reduced to one datum byte each (most significant
non-zero byte of the widening u16/u24/u32 idiom); stores sharing a
(frame, slot) are split into packets before every 0xae that follows other
data; within a tick, a leading [ae] or [ae, xx] prefix packet is joined
with the next non-ae-led packet from a higher slot (the FIGHT-call split
idiom). Ambiguous joins (heartbeat [ae] plus a lone suffix) are kept as
joined: the table records observed emission, not intent.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


WRITE = re.compile(
    r"^w f (\d+) addr=0x([0-9a-f]+) data=0x([0-9a-f]+) pc=(\S+)")
RING_BASE = 0x0051AA80
RING_END = 0x0051AABF
PRODUCER_PC = "0x2a4cc"


def datum(value: int) -> int:
    for shift in (0, 8, 16, 24):
        byte = (value >> shift) & 0xFF
        if byte and (value >> (shift + 8)) == 0 and (value & ((1 << shift) - 1)) == 0:
            return byte
    return value & 0xFF


def split_packets(values: list[int]) -> list[tuple[int, ...]]:
    packets: list[tuple[int, ...]] = []
    current: list[int] = []
    for byte in values:
        if byte == 0xAE and current and current != [0xAE]:
            packets.append(tuple(current))
            current = [byte]
        else:
            current.append(byte)
    if current:
        packets.append(tuple(current))
    return packets


def is_prefix(packet: tuple[int, ...]) -> bool:
    return packet == (0xAE,) or (len(packet) == 2 and packet[0] == 0xAE)


def extract(log: Path, spawns: list[int], window: int
            ) -> dict[int, list[dict[str, object]]]:
    groups: dict[tuple[int, int], list[int]] = defaultdict(list)
    for line in log.read_text(encoding="utf-8").splitlines():
        match = WRITE.match(line)
        if not match:
            continue
        frame, addr, data, pc = (int(match[1]), int(match[2], 16),
                                int(match[3], 16), match[4])
        if RING_BASE <= addr <= RING_END and pc == PRODUCER_PC:
            groups[(frame, addr)].append(datum(data))
    ticks: dict[int, list[tuple[int, tuple[int, ...]]]] = defaultdict(list)
    for (frame, addr), values in groups.items():
        for packet in split_packets(values):
            ticks[frame].append((addr, packet))
    scripts: dict[int, list[dict[str, object]]] = {}
    for index, spawn in enumerate(spawns, start=1):
        steps: list[dict[str, object]] = []
        for frame in sorted(ticks):
            if not (spawn - window <= frame <= spawn):
                continue
            items = sorted(ticks[frame])
            merged: list[tuple[int, ...]] = []
            cursor = 0
            while cursor < len(items):
                _, packet = items[cursor]
                if (is_prefix(packet) and cursor + 1 < len(items)
                        and items[cursor + 1][1][0] != 0xAE):
                    merged.append(packet + items[cursor + 1][1])
                    cursor += 2
                else:
                    merged.append(packet)
                    cursor += 1
            for packet in merged:
                steps.append({"offset": frame - spawn,
                              "bytes": list(packet)})
        scripts[index] = steps
    return scripts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", type=Path, required=True,
                        help="input-audio.log with the audio-ring write tap")
    parser.add_argument("--spawns", type=int, nargs="+",
                        default=[3178, 8009, 12841],
                        help="spawn frames delimiting stage windows")
    parser.add_argument("--window", type=int, default=130,
                        help="frames before spawn to include")
    parser.add_argument("--root", type=Path, default=Path.cwd(),
                        help="root the log path must remain within")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        args.log.resolve().relative_to(root)
    except (OSError, RuntimeError, ValueError):
        raise SystemExit(f"log path escapes root: {args.log}")
    if not args.log.is_file():
        raise SystemExit(f"missing log: {args.log}")
    print(json.dumps(extract(args.log, args.spawns, args.window), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
