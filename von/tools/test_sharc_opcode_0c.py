#!/usr/bin/env python3
"""Audit the three-input, normalized-vector SHARC service at opcode 0x0c."""

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
        "24e": "IF FLAG0_IN, JUMP",
        "24f": "R6 = DM(I0, M0)",
        "250": "IF FLAG0_IN, JUMP",
        "251": "F8 = F6 * F6,  R9 = DM(I0, M0)",
        "252": "IF FLAG0_IN, JUMP",
        "253": "F12 = F9 * F9,  R5 = DM(I0, M0)",
        "254": "F13 = F5 * F5",
        "255": "F8 = F8 + F12",
        "256": "F0 = F8 + F13",
        "257": "F4 = RSQRTS F0",
        "258": "F12 = F4 * F4",
        "25b": "F4 = F4 * F12",
        "264": "F0 = F6 * F4",
        "265": "IF FLAG1_IN, JUMP",
        "266": "F1 = F9 * F4,  DM(I1, M0) = R0",
        "267": "IF FLAG1_IN, JUMP",
        "268": "F2 = F5 * F4,  DM(I1, M0) = R1",
        "269": "IF FLAG1_IN, JUMP",
        "26a": "RTS (DB)",
        "26b": "DM(I1, M0) = R2",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0c slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x0c three-input RSQRT normalization and three-output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
