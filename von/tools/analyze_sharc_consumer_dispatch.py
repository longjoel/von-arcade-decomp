#!/usr/bin/env python3
"""Recover marker-slot dispatch from ordered marker read events.

The marker table can be read several times while one geometry frame is being
assembled.  A consumer PC is a stronger discriminator than temporal proximity:
if a PC is observed reading exactly one slot across the capture, it is a
validated slot dispatch.  PCs that read multiple slots remain unresolved.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def analyze(lines) -> dict:
    by_pc: dict[int, set[int]] = defaultdict(set)
    counts: dict[int, dict[int, int]] = defaultdict(lambda: defaultdict(int))
    for event in lines:
        if event.get("kind") != "marker_slot_consume":
            continue
        pc = int(event["pc"])
        slot = int(event["slot"])
        by_pc[pc].add(slot)
        counts[pc][slot] += 1

    dispatch = []
    ambiguous = []
    for pc in sorted(by_pc):
        slots = sorted(by_pc[pc])
        item = {
            "pc": f"0x{pc:08x}",
            "slots": slots,
            "reads": {str(slot): counts[pc][slot] for slot in slots},
        }
        (dispatch if len(slots) == 1 else ambiguous).append(item)

    return {
        "schema_version": 1,
        "policy": "marker-consumer-pc-v1",
        "dispatch": dispatch,
        "ambiguous": ambiguous,
        "validation": {
            "consumer_pcs": len(by_pc),
            "unique_dispatch_pcs": len(dispatch),
            "ambiguous_dispatch_pcs": len(ambiguous),
            "slot_0_pcs": sum(item["slots"] == [0] for item in dispatch),
            "slot_1_pcs": sum(item["slots"] == [1] for item in dispatch),
            "slot_2_pcs": sum(item["slots"] == [2] for item in dispatch),
            "slot_3_pcs": sum(item["slots"] == [3] for item in dispatch),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trace", type=Path, help="ordered transform NDJSON")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true",
                        help="fail if any consumer PC reads multiple slots")
    args = parser.parse_args()
    with args.trace.open(encoding="utf-8") as stream:
        # The ordered capture also contains millions of FIFO events. Avoid
        # decoding those when only marker-consume records can affect this
        # report.
        events = (json.loads(line) for line in stream
                  if '"kind":"marker_slot_consume"' in line)
        result = analyze(events)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["validation"], sort_keys=True, separators=(",", ":")))
    if args.check and result["ambiguous"]:
        raise SystemExit("marker consumer dispatch is ambiguous")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
