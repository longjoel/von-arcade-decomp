#!/usr/bin/env python3
"""Audit the eight-input SHARC projection/state service at opcode 0x31."""

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

    for slot, register in zip(("763", "765", "767", "769", "76b", "76d", "76f", "771"), ("R5", "R6", "R7", "R10", "R9", "R13", "R14", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x31 slot {slot} missing {register} FIFO read")
    for slot in ("762", "764", "766", "768", "76a", "76c", "76e", "770"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x31 slot {slot} missing FIFO wait")

    checks = {
        "772": "I7 = 0x00030180",
        "773": "R0 = 0x00000000",
        "774": "R1 = 0x3F800000",
        "775": "DM(0x00000000, I7) = R1",
        "77d": "DM(0x00000008, I7) = R1",
        "77e": "DM(0x00000009, I7) = R5",
        "77f": "DM(0x0000000A, I7) = R6",
        "780": "DM(0x0000000B, I7) = R7",
        "781": "R0 = LSHIFT R10 BY 16",
        "784": "R1 = 0x38C9116D",
        "785": "CALL (0x00020DBE) (DB)",
        "788": "CALL (0x00020DC4) (DB)",
        "78b": "I7 = 0x00030180",
        "78e": "F9 = F1 * F4,  R4 = DM(0x00, I7)",
        "791": "DM(0x00, I7) = R8",
        "793": "DM(0x06, I7) = R9",
        "795": "DM(0x01, I7) = R10",
        "799": "DM(0x02, I7) = R8",
        "79a": "R0 = LSHIFT R5 BY 16",
        "79e": "CALL (0x00020DBE) (DB)",
        "7a1": "CALL (0x00020DC4) (DB)",
        "7a4": "I7 = 0x00030180",
        "7aa": "DM(0x03, I7) = R8",
        "7ac": "DM(0x06, I7) = R9",
        "7ae": "DM(0x04, I7) = R10",
        "7b2": "DM(0x05, I7) = R8",
        "7b3": "DM(0x00000008, I7) = R9",
        "7b4": "R8 = DM(0x00000009, I7)",
        "7b6": "R10 = DM(0x0000000B, I7)",
        "7c0": "IF FLAG1_IN, JUMP",
        "7c1": "DM(I1, M0) = R8",
        "7c3": "DM(I1, M0) = R9",
        "7c5": "RTS (DB)",
        "7c6": "DM(I1, M0) = R10",
        "7c8": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x31 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x31 projection/state service contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
