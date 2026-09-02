#!/usr/bin/env python3
"""Audit the five-input SHARC matrix setup/update service at opcode 0x30."""

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

    for slot, register in zip(("712", "714", "716", "718", "71a"), ("R0", "R1", "R2", "R15", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x30 slot {slot} missing {register} FIFO read")
    for slot in ("711", "713", "715", "717", "719"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x30 slot {slot} missing FIFO wait")

    checks = {
        "71b": "I7 = DM(0x00030101)",
        "71c": "R8 = DM(0x00000009, I7)",
        "71e": "R10 = DM(0x0000000B, I7)",
        "728": "DM(0x09, I7) = R8",
        "72a": "DM(0x0000000A, I7) = R9",
        "72b": "DM(0x0000000B, I7) = R10",
        "72c": "R0 = 0x00000000",
        "72d": "R1 = 0x3F800000",
        "72e": "DM(0x00000000, I7) = R1",
        "732": "DM(0x00000004, I7) = R1",
        "738": "DM(0x08, I7) = R1",
        "739": "R1 = 0x38C9116D",
        "73a": "CALL (0x00020DBE) (DB)",
        "73d": "CALL (0x00020DC4) (DB)",
        "740": "I7 = DM(0x00030101)",
        "746": "DM(0x00, I7) = R7",
        "748": "DM(0x03, I7) = R9",
        "74a": "DM(0x01, I7) = R10",
        "74e": "DM(0x02, I7) = R8",
        "74f": "DM(0x00000005, I7) = R9",
        "75e": "DM(0x06, I7) = R1",
        "75f": "RTS (DB)",
        "760": "DM(0x00000007, I7) = R2",
        "761": "DM(0x00000008, I7) = R3",
        "762": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x30 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x30 matrix setup/update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
