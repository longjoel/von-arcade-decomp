#!/usr/bin/env python3
"""Compare an ordered matrix/object geometry-event prefix between two logs."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EVENT = re.compile(r"vonj_geometry_(matrix|object): time=[^ ]+ (.*)")


def events(path: Path) -> list[tuple[str, str]]:
    result = []
    for line in path.read_text(errors="replace").splitlines():
        match = EVENT.search(line)
        if match:
            result.append((match[1], match[2]))
    return result


def compare(original: Path, reconstructed: Path, limit: int) -> tuple[int, str | None]:
    left = events(original)[:limit]
    right = events(reconstructed)[:limit]
    if len(left) < limit:
        return len(left), f"original has only {len(left)} geometry events (need {limit})"
    if len(right) < limit:
        return len(right), f"reconstructed has only {len(right)} geometry events (need {limit})"
    for index, (expected, actual) in enumerate(zip(left, right)):
        if expected != actual:
            return index, f"event {index} differs: expected {expected!r}, got {actual!r}"
    return limit, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, required=True)
    parser.add_argument("--reconstructed", type=Path, required=True)
    parser.add_argument("--events", type=int, default=13)
    args = parser.parse_args()
    count, error = compare(args.original, args.reconstructed, args.events)
    if error:
        print(f"geometry event prefix: FAIL after {count} event(s): {error}")
        return 1
    print(f"geometry event prefix: PASS ({count} ordered events)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
