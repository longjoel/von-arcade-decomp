#!/usr/bin/env python3
"""Summarize bounded Virtual-On MAME boundary events from an oslog trace."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


EVENT_RE = re.compile(r"^\[[^]]+\]\s+(?P<event>\w+):\s+(?P<body>.*)$")
SAMPLE_RE = re.compile(r"^sample=(?P<body>.*)$")
FIELD_RE = re.compile(r"(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>[^ ]+)")
FIFO_RE = re.compile(r"data=(?P<data>[0-9a-fA-F]+)")
GEO_RE = re.compile(r"pc=(?P<pc>[0-9a-fA-F]+) address=(?P<address>[0-9a-fA-F]+) data=(?P<data>[0-9a-fA-F]+)")


def fields(body: str) -> dict[str, str | int | float]:
    result: dict[str, str | int | float] = {}
    hexadecimal = {"pc", "address", "data", "read", "write", "slot", "byte", "value"}
    for match in FIELD_RE.finditer(body):
        key, value = match.group("key"), match.group("value")
        try:
            if key == "time":
                result[key] = float(value)
            elif key in hexadecimal:
                result[key] = int(value, 16)
            elif value.isdigit():
                result[key] = int(value)
            else:
                result[key] = value
        except ValueError:
            result[key] = value
    return result


def ndjson_event(line: str, seq: int) -> dict | None:
    match = EVENT_RE.match(line)
    if match:
        event = {"seq": seq, "kind": match.group("event")}
        event.update(fields(match.group("body")))
        return event
    sample = SAMPLE_RE.match(line)
    if sample:
        event = {"seq": seq, "kind": "audio-queue-sample"}
        event.update(fields(sample.group("body")))
        return event
    return None


def select_events(events: list[dict], max_events: int | None = None,
                  event_kinds: set[str] | None = None,
                  pc_min: int | None = None, pc_max: int | None = None) -> list[dict]:
    selected = []
    for event in events:
        if event_kinds and event.get("kind") not in event_kinds:
            continue
        pc = event.get("pc")
        if pc_min is not None and (not isinstance(pc, int) or pc < pc_min):
            continue
        if pc_max is not None and (not isinstance(pc, int) or pc > pc_max):
            continue
        selected.append(event)
        if max_events is not None and len(selected) >= max_events:
            break
    for seq, event in enumerate(selected):
        event["seq"] = seq
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    parser.add_argument("--ndjson", type=Path,
                        help="also write normalized ordered events")
    parser.add_argument("--max-events", type=int)
    parser.add_argument("--event-kind", action="append", default=[])
    parser.add_argument("--pc-min", type=lambda value: int(value, 0))
    parser.add_argument("--pc-max", type=lambda value: int(value, 0))
    args = parser.parse_args()

    counts: Counter[str] = Counter()
    fifo: list[tuple[int, str, str]] = []
    geo: list[tuple[int, str, str, str]] = []
    tile_count = 0

    normalized: list[dict] = []
    for line_number, line in enumerate(args.trace.read_text(errors="replace").splitlines(), 1):
        event_record = ndjson_event(line, len(normalized))
        if event_record is not None:
            event_record["source_line"] = line_number
            normalized.append(event_record)
        match = EVENT_RE.match(line)
        if not match:
            continue
        event = match.group("event")
        body = match.group("body")
        counts[event] += 1
        if event == "vonj_copro_fifo":
            data = FIFO_RE.search(body)
            if data:
                pc = re.search(r"pc=([0-9a-fA-F]+)", body)
                fifo.append((line_number, pc.group(1) if pc else "?", data.group("data")))
        elif event == "vonj_geo_cmd":
            match_geo = GEO_RE.search(body)
            if match_geo:
                geo.append((line_number, match_geo.group("pc"), match_geo.group("address"), match_geo.group("data")))
        elif event == "vonj_tile_write":
            tile_count += 1

    print("Event counts:")
    for event, count in sorted(counts.items()):
        print(f"  {event}: {count}")

    print("FIFO sequence:")
    for line_number, pc, data in fifo:
        print(f"  line={line_number} pc={pc} data={data}")

    print("First Geo events:")
    for line_number, pc, address, data in geo[:32]:
        print(f"  line={line_number} pc={pc} address={address} data={data}")

    print(f"Tile writes: {tile_count}")
    if args.ndjson:
        normalized = select_events(normalized, args.max_events, set(args.event_kind), args.pc_min, args.pc_max)
        args.ndjson.parent.mkdir(parents=True, exist_ok=True)
        args.ndjson.write_text(
            "".join(json.dumps(event, sort_keys=True) + "\n" for event in normalized),
            encoding="utf-8",
        )
        print(f"Normalized events: {len(normalized)} -> {args.ndjson}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
