#!/usr/bin/env python3
"""Audit the SHARC matrix reset/parameterized state initializer at opcode 0x29."""

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

    for slot, register in zip(("5aa", "5ac", "5ae", "5b0"), ("R13", "R14", "R15", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x29 slot {slot} missing {register} FIFO read")
    for slot in ("5a9", "5ab", "5ad", "5af"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x29 slot {slot} missing FIFO wait")

    checks = {
        "5b1": "I7 = DM(0x00030101)",
        "5b2": "R0 = 0x00000000",
        "5b3": "R1 = 0x3F800000",
        "5b4": "DM(0x00000000, I7) = R1",
        "5b8": "DM(0x00000004, I7) = R1",
        "5bc": "DM(0x00000008, I7) = R1",
        "5bd": "DM(0x00000009, I7) = R13",
        "5be": "DM(0x0000000A, I7) = R14",
        "5bf": "DM(0x0000000B, I7) = R15",
        "5c0": "R0 = LSHIFT R2 BY 16",
        "5c1": "R0 = ASHIFT R0 BY -16",
        "5c2": "F0 = FLOAT R0",
        "5c3": "R1 = 0x38C9116D",
        "5c4": "CALL (0x00020DBE) (DB)",
        "5c7": "CALL (0x00020DC4) (DB)",
        "5ca": "I7 = DM(0x00030101)",
        "5d0": "DM(0x00, I7) = R8",
        "5d2": "DM(0x06, I7) = R9",
        "5d4": "DM(0x01, I7) = R10",
        "5d6": "DM(0x07, I7) = R11",
        "5d7": "RTS (DB)",
        "5d9": "DM(0x00000008, I7) = R9",
        "5da": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x29 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x29 matrix reset/parameterized initializer contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
