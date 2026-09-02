#!/usr/bin/env python3
"""Audit the five-input SHARC matrix update at opcode 0x33."""

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

    for slot, register in zip(("845", "847", "849", "84b", "84d"), ("R0", "R1", "R2", "R14", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x33 slot {slot} missing {register} FIFO read")
    for slot in ("844", "846", "848", "84a", "84c"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x33 slot {slot} missing FIFO wait")

    checks = {
        "84e": "I7 = DM(0x00030101)",
        "84f": "R8 = DM(0x00000009, I7)",
        "851": "R10 = DM(0x0000000B, I7)",
        "85b": "DM(0x09, I7) = R8",
        "85c": "DM(0x0A, I7) = R9",
        "85f": "DM(0x0B, I7) = R10",
        "860": "R1 = 0x38C9116D",
        "861": "CALL (0x00020DBE) (DB)",
        "864": "CALL (0x00020DC4) (DB)",
        "867": "I7 = DM(0x00030101)",
        "86d": "DM(0x00, I7) = R8",
        "86f": "DM(0x06, I7) = R9",
        "871": "DM(0x01, I7) = R10",
        "875": "DM(0x02, I7) = R8",
        "876": "R0 = LSHIFT R13 BY 16",
        "87a": "CALL (0x00020DBE) (DB)",
        "87d": "CALL (0x00020DC4) (DB)",
        "880": "I7 = DM(0x00030101)",
        "886": "DM(0x03, I7) = R8",
        "888": "DM(0x06, I7) = R9",
        "88a": "DM(0x04, I7) = R10",
        "88e": "DM(0x05, I7) = R8",
        "88d": "RTS (DB)",
        "88f": "DM(0x00000008, I7) = R9",
        "890": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x33 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x33 five-input matrix update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
