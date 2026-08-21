#!/usr/bin/env python3
"""Pack transported SHARC 48-bit words into MAME's 64-bit program slots."""

from __future__ import annotations

import argparse
from pathlib import Path


SLOT_PAYLOAD_SIZE = 6
SLOT_SIZE = 8


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    payload = args.input.read_bytes()
    slots = bytearray()
    for offset in range(0, len(payload), SLOT_PAYLOAD_SIZE):
        chunk = payload[offset : offset + SLOT_PAYLOAD_SIZE]
        slots.extend(chunk)
        slots.extend(b"\0" * (SLOT_PAYLOAD_SIZE - len(chunk)))
        slots.extend(b"\0\0")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(slots)
    print(f"Wrote {len(slots) // SLOT_SIZE} 64-bit program slots to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
