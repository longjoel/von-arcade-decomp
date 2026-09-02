#!/usr/bin/env python3
"""Audit the four-input SHARC state service at opcode 0x36."""

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

    for slot, register in zip(("90a", "90c", "90e", "910"), ("R0", "R1", "R2", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x36 slot {slot} missing {register} FIFO read")
    for slot in ("909", "90b", "90d", "90f"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x36 slot {slot} missing FIFO wait")

    checks = {
        "911": "I7 = DM(0x00030101)",
        "912": "R8 = DM(0x00000009, I7)",
        "914": "R10 = DM(0x0000000B, I7)",
        "91e": "DM(0x09, I7) = R8",
        "920": "DM(0x0000000A, I7) = R9",
        "921": "DM(0x0000000B, I7) = R10",
        "922": "R0 = 0x00000000",
        "923": "R4 = 0x3F800000",
        "924": "DM(0x00000000, I7) = R4",
        "928": "DM(0x00000004, I7) = R4",
        "92c": "DM(0x00000008, I7) = R4",
        "92d": "R0 = R13",
        "930": "DM(0x00, I7) = R1",
        "932": "DM(0x00000002, I7) = R3",
        "936": "DM(0x03, I7) = R1",
        "938": "DM(0x00000005, I7) = R3",
        "93c": "DM(0x06, I7) = R1",
        "93d": "RTS (DB)",
        "93e": "DM(0x00000007, I7) = R2",
        "93f": "DM(0x00000008, I7) = R3",
        "940": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x36 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x36 four-input state contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
