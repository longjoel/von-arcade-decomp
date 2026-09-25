#!/usr/bin/env python3
"""Join i960 packet writes to the SHARC FIFO words actually consumed.

The two traces run on different CPUs, so wall-clock timestamps are not a
reliable join key.  Both taps share the monotonically increasing event_id;
this tool verifies that each packet's command stream appears in the SHARC
read stream in order and reports the exact read event ids.  It intentionally
does not reinterpret matrix math: that remains the independent commit
verifier's job.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("--frame", type=int)
    args = parser.parse_args()

    events = []
    with args.trace.open() as stream:
        for line in stream:
            event = json.loads(line)
            if args.frame is None or event.get("frame") == args.frame:
                events.append(event)

    reads = [e for e in events if e.get("kind") == "sharc_fifo_read"]
    packets = []
    pending = []
    for event in events:
        if event.get("kind") == "i960_fifo":
            # Fighter transform packets begin with command 5.  Other FIFO
            # traffic shares the tap and must not be folded into a packet.
            if not pending:
                if event.get("data") != 5:
                    continue
                pending = [event]
                continue
            pending.append(event)
            if event.get("data") == 6:
                # A packet terminates at opcode 6.  Keep command words and
                # record the event id of the first word for stable joins.
                packets.append(pending)
                pending = []

    cursor = 0
    matched = 0
    mismatches = 0
    report = []
    for packet in packets:
        words = [e["data"] & 0xffffffff for e in packet]
        found = None
        for i in range(cursor, len(reads) - len(words) + 1):
            if [e["data"] & 0xffffffff for e in reads[i:i + len(words)]] == words:
                found = i
                break
        if found is None:
            mismatches += 1
            continue
        consumed = reads[found:found + len(words)]
        cursor = found + len(words)
        matched += 1
        report.append({
            "packet_event_id": packet[0]["event_id"],
            "read_event_ids": [e["event_id"] for e in consumed],
            "read_pc": [e.get("pc") for e in consumed],
            "words": words,
        })

    print(json.dumps({
        "frame": args.frame,
        "packets": len(packets),
        "reads": len(reads),
        "matched": matched,
        "mismatches": mismatches,
        "joins": report,
    }, separators=(",", ":")))
    return 0 if mismatches == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
