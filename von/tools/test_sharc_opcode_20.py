#!/usr/bin/env python3
"""Audit the three-word state-tail readback service at opcode 0x20."""

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
        "40a": "I7 = DM(0x00030101)",
        "40b": "R0 = DM(0x00000009, I7)",
        "40c": "IF FLAG1_IN, JUMP",
        "40d": "DM(I1, M0) = R0",
        "40e": "R1 = DM(0x0000000A, I7)",
        "40f": "IF FLAG1_IN, JUMP",
        "410": "DM(I1, M0) = R1",
        "411": "IF FLAG1_IN, JUMP",
        "412": "RTS (DB)",
        "413": "R2 = DM(0x0000000B, I7)",
        "414": "DM(I1, M0) = R2",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x20 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x20 three-word state-tail readback contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
