#!/usr/bin/env python3
"""Audit the three-input SHARC state reset service at opcode 0x37."""

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

    for slot, register in zip(("941", "943", "945"), ("R13", "R14", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x37 slot {slot} missing {register} FIFO read")
    for slot in ("940", "942", "944"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x37 slot {slot} missing FIFO wait")

    checks = {
        "946": "I7 = DM(0x00030101)",
        "947": "R0 = 0x00000000",
        "948": "R1 = 0x3F800000",
        "949": "DM(0x00000000, I7) = R1",
        "94d": "DM(0x00000004, I7) = R1",
        "951": "DM(0x00000008, I7) = R1",
        "952": "DM(0x00000009, I7) = R13",
        "953": "RTS (DB)",
        "954": "DM(0x0000000A, I7) = R14",
        "955": "DM(0x0000000B, I7) = R15",
        "956": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x37 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x37 three-input state reset contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
