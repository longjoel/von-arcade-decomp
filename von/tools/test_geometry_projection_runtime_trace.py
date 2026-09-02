#!/usr/bin/env python3
"""Validate the recorded runtime shape of the 0x6f6f0 response path."""

from __future__ import annotations

import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "von/build/disasm/vonj-geometry-select-50s.trace"
EVENT = re.compile(r"vonj_geometry_response: pc=([0-9a-f]+) data=([0-9a-f]+)")
REQUEST = re.compile(r"vonj_copro_fifo: pc=0006f7a8 data=([0-9a-f]+)")
PROJECTION_PCS = {
    "0006f7ac": "lookup",
    "0006f7b4": "middle",
    "0006f818": "final",
}


def main() -> int:
    events: list[tuple[str, int]] = []
    pending_index: int | None = None
    indexed_middle: list[tuple[int, int]] = []
    for line in TRACE.read_text(encoding="utf-8").splitlines():
        request = REQUEST.search(line)
        if request:
            pending_index = int(request.group(1), 16)
        match = EVENT.search(line)
        if match and match.group(1) in PROJECTION_PCS:
            kind = PROJECTION_PCS[match.group(1)]
            value = int(match.group(2), 16)
            events.append((kind, value))
            if kind == "middle" and pending_index is not None:
                indexed_middle.append((pending_index, value))

    if len(events) % 3:
        raise SystemExit("projection response stream is not divisible into triplets")

    triplets = [events[offset : offset + 3] for offset in range(0, len(events), 3)]
    if not triplets:
        raise SystemExit("projection response stream is empty")
    if any([event[0] for event in triplet] != ["lookup", "middle", "final"] for triplet in triplets):
        raise SystemExit("projection response PCs no longer form lookup/middle/final triplets")

    lookup_values = Counter(triplet[0][1] for triplet in triplets)
    middle_values = Counter(triplet[1][1] for triplet in triplets)
    final_values = Counter(triplet[2][1] for triplet in triplets)
    if lookup_values != Counter({0: len(triplets)}):
        raise SystemExit(f"unexpected lookup response values: {lookup_values}")
    if set(middle_values) - {0, 6, 13}:
        raise SystemExit(f"unexpected middle response values: {middle_values}")
    if final_values != Counter({0: len(triplets)}):
        raise SystemExit(f"unexpected final response values: {final_values}")
    representative_values = dict(indexed_middle)
    expected_representatives = {
        0x0000BE7C: 0,
        0x0000C079: 13,
        0x000138AF: 6,
        0x00023D04: 13,
    }
    for request_index, expected in expected_representatives.items():
        if representative_values.get(request_index) != expected:
            raise SystemExit(
                f"request index 0x{request_index:08x} did not produce {expected}"
            )

    print(
        "PASS: projection trace has "
        f"{len(triplets)} lookup/middle/final triplets; "
        f"middle values={dict(sorted(middle_values.items()))}; "
        f"indexed samples={len(indexed_middle)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
