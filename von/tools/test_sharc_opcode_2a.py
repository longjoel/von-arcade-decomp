#!/usr/bin/env python3
"""Audit the one-input SHARC persistent-matrix scale at opcode 0x2a."""

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

    if "R0 = DM(I0, M0)" not in lines.get("5db", ""):
        raise SystemExit("SHARC opcode-0x2a missing scalar FIFO read")
    if "IF FLAG0_IN, JUMP" not in lines.get("5da", ""):
        raise SystemExit("SHARC opcode-0x2a missing FIFO wait")

    checks = {
        "5dc": "I7 = DM(0x00030101)",
        "5dd": "R4 = DM(0x00000000, I7)",
        "5de": "F1 = F0 * F4,  R4 = DM(0x01, I7)",
        "5df": "F2 = F0 * F4,  R4 = DM(0x02, I7)",
        "5e0": "F3 = F0 * F4,  DM(0x00, I7) = R1",
        "5e1": "DM(0x00000001, I7) = R2",
        "5e2": "DM(0x00000002, I7) = R3",
        "5e6": "DM(0x03, I7) = R1",
        "5e8": "DM(0x00000005, I7) = R3",
        "5ec": "DM(0x06, I7) = R1",
        "5ed": "RTS (DB)",
        "5ee": "DM(0x00000007, I7) = R2",
        "5ef": "DM(0x00000008, I7) = R3",
        "5f0": "IF FLAG1_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2a slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x2a persistent-matrix scale contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
