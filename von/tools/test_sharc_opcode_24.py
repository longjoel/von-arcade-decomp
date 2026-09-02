#!/usr/bin/env python3
"""Audit the three-input SHARC fixed-point projection at opcode 0x24."""

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

    for slot, register in zip(("4be", "4c0", "4c2"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x24 slot {slot} missing {register} FIFO read")
    for slot in ("4bd", "4bf", "4c1"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x24 slot {slot} missing FIFO wait")

    checks = {
        "4c3": "I7 = DM(0x00030101)",
        "4c9": "F4 = RSQRTS F0",
        "4e7": "R4 = DM(0x00, I7)",
        "4e8": "R4 = DM(0x06, I7)",
        "4e9": "R5 = DM(0x01, I7)",
        "4f3": "R5 = DM(0x03, I7)",
        "4f7": "DM(0x00000008, I7) = R9",
        "507": "RTS (DB)",
        "509": "DM(0x00000008, I7) = R9",
        "50a": "IF FLAG0_IN, JUMP (0x0000050A)",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x24 slot {slot} missing {fragment}")

    # Opening pass: the three FIFO lanes are squared and accumulated before
    # the reciprocal-square-root normalization path.
    for slot, fragment in {
        "4c5": "F8 = F0 * F4",
        "4c6": "F12 = F2 * F4",
        "4c7": "F12 = F1 * F4",
        "4c8": "F8 = F8 + F12",
        "4c9": "F4 = RSQRTS F0",
        "4d6": "F5 = F5 * F4",
        "4d7": "F0 = F0 * F4",
        "4d8": "F2 = F2 * F4",
        "4e6": "F1 = F1 * F4",
    }.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x24 normalization slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x24 normalized frame-update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
