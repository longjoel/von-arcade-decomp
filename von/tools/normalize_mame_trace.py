#!/usr/bin/env python3
"""Summarize bounded Virtual-On MAME boundary events from an oslog trace."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path


EVENT_RE = re.compile(r"^\[[^]]+\]\s+(?P<event>\w+):\s+(?P<body>.*)$")
FIFO_RE = re.compile(r"data=(?P<data>[0-9a-fA-F]+)")
GEO_RE = re.compile(r"pc=(?P<pc>[0-9a-fA-F]+) address=(?P<address>[0-9a-fA-F]+) data=(?P<data>[0-9a-fA-F]+)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path)
    args = parser.parse_args()

    counts: Counter[str] = Counter()
    fifo: list[tuple[int, str, str]] = []
    geo: list[tuple[int, str, str, str]] = []
    tile_count = 0

    for line_number, line in enumerate(args.trace.read_text(errors="replace").splitlines(), 1):
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
