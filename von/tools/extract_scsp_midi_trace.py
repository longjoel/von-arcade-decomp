#!/usr/bin/env python3
"""Extract timestamped sound-CPU MIDI bytes from a MAME log.

This preserves the command evidence already present in runtime traces.  It is
not an SCSP descriptor extractor: the log contains MIDI bytes, but usually not
the later SA/LSA/LEA register writes needed for exact sample boundaries.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


TIME = re.compile(r"time=([0-9]+(?:\.[0-9]+)?)")
MIDI = re.compile(r"\[:scsp\] Read ([0-9a-fA-F]{1,2}) from SCSP MIDI")


def extract(path: Path) -> dict:
    current_time = 0.0
    pending: list[dict] = []
    events: list[dict] = []
    byte_count = 0
    for line_number, line in enumerate(path.read_text(errors="replace").splitlines(), 1):
        match = TIME.search(line)
        if match:
            current_time = float(match.group(1))
        match = MIDI.search(line)
        if not match:
            continue
        pending.append({"line": line_number, "time": current_time,
                        "byte": int(match.group(1), 16)})
        byte_count += 1
        if len(pending) == 3:
            events.append({
                "time": pending[0]["time"],
                "line": pending[0]["line"],
                "bytes": [item["byte"] for item in pending],
                "raw": " ".join(f'{item["byte"]:02x}' for item in pending),
            })
            pending = []
    return {
        "source": str(path),
        "format": "MAME SCSP MIDI reads grouped into three-byte packets",
        "byte_count": byte_count,
        "packet_count": len(events),
        "partial_bytes": [item["byte"] for item in pending],
        "events": events,
        "notes": [
            "Timestamps are the most recent timestamp-bearing log line before each MIDI byte.",
            "This trace identifies sound commands and timing, not SCSP SA/LSA/LEA sample ranges.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("log", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    report = extract(args.log)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {args.output} ({report['packet_count']} packets, {report['byte_count']} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
