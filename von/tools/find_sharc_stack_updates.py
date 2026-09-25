#!/usr/bin/env python3
"""Report SHARC stack bases that change between sibling pushes.

The Lua transform tap records push/pop pointers, but not the service opcode
that mutates the live matrix.  A changed base at the same depth is therefore
an explicit capture requirement: it must not be promoted to a fitted parent.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--frame", type=int)
    args = parser.parse_args()

    last_by_depth: dict[int, tuple[int, ...]] = {}
    writes_since_push: list[dict[str, int]] = []
    changes = []
    for line in args.capture.open():
        event = json.loads(line)
        if event.get("kind") == "sharc_service_write":
            if args.frame is None or event.get("frame") == args.frame:
                depth = event.get("depth")
                writes_since_push.append({
                    key: event[key] for key in ("event_id", "pc", "offset", "data")
                })
            continue
        if event.get("kind") not in ("push", "pop"):
            continue
        if args.frame is not None and event.get("frame") != args.frame:
            continue
        depth = event.get("depth")
        if event["kind"] == "push":
            words = tuple(event["base_words"])
            previous = last_by_depth.get(depth)
            if previous is not None and previous != words:
                changes.append({
                    "event_id": event["event_id"],
                    "frame": event.get("frame"),
                    "depth": depth,
                    "previous_base_words": list(previous),
                    "base_words": list(words),
                    "service_writes_since_previous_push": writes_since_push,
                })
            writes_since_push = []
            last_by_depth[depth] = words
    print(json.dumps({"schema_version": 1, "changes": changes},
                     sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
