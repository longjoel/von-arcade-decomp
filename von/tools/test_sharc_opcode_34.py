#!/usr/bin/env python3
"""Audit the eight-input SHARC persistent-state rebuild at opcode 0x34."""

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

    for slot, register in zip(("891", "893", "895", "897", "899", "89b", "89d", "89f"), ("R0", "R1", "R2", "R5", "R6", "R13", "R14", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x34 slot {slot} missing {register} FIFO read")
    for slot in ("890", "892", "894", "896", "898", "89a", "89c", "89e"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x34 slot {slot} missing FIFO wait")

    checks = {
        "8a0": "I7 = DM(0x00030101)",
        "8a1": "R8 = DM(0x00000009, I7)",
        "8a3": "R10 = DM(0x0000000B, I7)",
        "8ad": "DM(0x09, I7) = R8",
        "8ae": "DM(0x0A, I7) = R9",
        "8b1": "DM(0x0B, I7) = R10",
        "8b2": "R1 = 0x38C9116D",
        "8b3": "CALL (0x00020DBE) (DB)",
        "8b6": "CALL (0x00020DC4) (DB)",
        "8b9": "I7 = DM(0x00030101)",
        "8bf": "DM(0x00, I7) = R8",
        "8c1": "DM(0x06, I7) = R9",
        "8c3": "DM(0x01, I7) = R10",
        "8c7": "DM(0x02, I7) = R8",
        "8c8": "R0 = LSHIFT R6 BY 16",
        "8cc": "CALL (0x00020DBE) (DB)",
        "8cf": "CALL (0x00020DC4) (DB)",
        "8d2": "I7 = DM(0x00030101)",
        "8d8": "DM(0x03, I7) = R8",
        "8da": "DM(0x06, I7) = R9",
        "8dc": "DM(0x04, I7) = R10",
        "8e0": "DM(0x05, I7) = R8",
        "8df": "R1 = R13",
        "8dd": "R4 = DM(0x08, I7)",
        "8de": "DM(0x07, I7) = R11",
        "8ef": "RTS (DB)",
        "8f0": "DM(0x0A, I7) = R9",
        "8f1": "DM(0x0000000B, I7) = R10",
        "8f2": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x34 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x34 eight-input state rebuild contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
