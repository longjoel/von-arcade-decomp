#!/usr/bin/env python3
"""Validate opcode 0x4d's pre-angle dataflow into helper 0x20d68."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    # d00/d01 preserve the signed Y difference in F0 while forming dx²;
    # d05 copies F2 (dz) into F4, so d06/d07 add dz².
    checks = {
        "cfd": "F0 = F8 - F12",
        "d00": "F8 = F0 * F4,  F1 = F9 - F13",
        "d01": "F0 = PASS F1",
        "d05": "R4 = R2",
        "d06": "F12 = F2 * F4",
        "d07": "F1 = F8 + F12",
        # Refine reciprocal sqrt(seed), then form sqrt(seed) in F1 before the
        # delayed call.  F0 remains dy, so helper 0x20d68 receives (dy, sqrt(seed)).
        "d08": "F4 = RSQRTS F1",
        "d14": "CALL (0x00020D68)",
        "d15": "F4 = F4 * F12",
        "d16": "F1 = F1 * F4",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4d angle setup slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x4d angle-helper caller contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
