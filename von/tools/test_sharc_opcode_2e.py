#!/usr/bin/env python3
"""Audit the packed-parameter SHARC matrix rebuild at opcode 0x2e."""

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

    for slot, register in zip(("662", "664", "666", "668", "66a", "66c"), ("R0", "R1", "R2", "R13", "R14", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2e slot {slot} missing {register} FIFO read")
    for slot in ("661", "663", "665", "667", "669", "66b"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2e slot {slot} missing FIFO wait")

    checks = {
        "667": "IF FLAG0_IN, JUMP",
        "66d": "I7 = DM(0x00030101)",
        "66e": "I6 = 0x00030141",
        "66f": "R5 = LSHIFT R0 BY 16",
        "679": "R5 = LSHIFT R1 BY 16",
        "682": "R5 = LSHIFT R2 BY 16",
        "695": "R0 = LSHIFT R15 BY 24",
        "6ae": "R0 = LSHIFT R14 BY 24",
        "6c7": "R0 = LSHIFT R13 BY 24",
        "671": "R8 = DM(0x00000000, I6)",
        "672": "R6 = R6 AND R8",
        "673": "R0 = R5 AND R7",
        "679": "R5 = LSHIFT R1 BY 16",
        "682": "R5 = LSHIFT R2 BY 16",
        "689": "R8 = DM(0x09, I7)",
        "693": "DM(0x09, I7) = R8",
        "697": "DM(0x0B, I7) = R10",
        "698": "R1 = 0x38C9116D",
        "699": "CALL (0x00020DBE) (DB)",
        "69c": "CALL (0x00020DC4) (DB)",
        "69f": "I7 = DM(0x00030101)",
        "6a5": "DM(0x00, I7) = R8",
        "6a7": "DM(0x03, I7) = R9",
        "6a9": "DM(0x01, I7) = R10",
        "6ad": "DM(0x02, I7) = R8",
        "6ae": "R0 = LSHIFT R14 BY 24",
        "6b2": "CALL (0x00020DBE) (DB)",
        "6b5": "CALL (0x00020DC4) (DB)",
        "6c7": "R0 = LSHIFT R13 BY 24",
        "6cb": "CALL (0x00020DBE) (DB)",
        "6ce": "CALL (0x00020DC4) (DB)",
        "6d1": "I7 = DM(0x00030101)",
        "6d7": "DM(0x03, I7) = R8",
        "6d9": "DM(0x06, I7) = R9",
        "6db": "DM(0x04, I7) = R10",
        "6df": "DM(0x05, I7) = R8",
        "6de": "RTS (DB)",
        "6e0": "DM(0x00000008, I7) = R9",
        "6e1": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2e slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x2e packed-parameter matrix rebuild contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
