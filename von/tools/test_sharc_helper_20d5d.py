#!/usr/bin/env python3
"""Audit the SHARC helper that derives the state/table base pointers."""

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

    checks = {
        "d5d": "M7 = R0",
        "d5e": "I7 = 0x01C00010",
        "d5f": "R1 = 0x01C00000",
        "d60": "R0 = DM(M7, I7)",
        "d61": "R0 = R0 + R1",
        "d62": "DM(0x00030103) = R0",
        "d63": "I7 = 0x01C00020",
        "d64": "R0 = DM(M7, I7)",
        "d65": "RTS (DB)",
        "d66": "R0 = R0 + R1",
        "d67": "DM(0x00030104) = R0",
        "d68": "I7 = 0x00030300",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20d5d slot {slot} missing {fragment}")

    print("PASS: SHARC helper-0x20d5d table/state base derivation contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
