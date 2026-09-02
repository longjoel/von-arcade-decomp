#!/usr/bin/env python3
"""Audit the six-input SHARC parameterized matrix rebuild at opcode 0x2c."""

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

    for slot, register in zip(("5f5", "5f7", "5f9", "5fb", "5fd", "5ff"), ("R0", "R1", "R2", "R13", "R14", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2c slot {slot} missing {register} FIFO read")
    for slot in ("5f4", "5f6", "5f8", "5fa", "5fc", "5fe"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2c slot {slot} missing FIFO wait")

    checks = {
        "600": "I7 = DM(0x00030101)",
        "605": "F12 = F0 * F4,  R4 = DM(0x01, I7)",
        "608": "F12 = F1 * F4,  F10 = F10 + F12",
        "601": "R8 = DM(0x00000009, I7)",
        "602": "R9 = DM(0x0000000A, I7)",
        "603": "R10 = DM(0x0000000B, I7)",
        "60d": "DM(0x09, I7) = R8",
        "60e": "DM(0x0A, I7) = R9",
        "611": "DM(0x0B, I7) = R10",
        "612": "R1 = 0x38C9116D",
        "613": "CALL (0x00020DBE) (DB)",
        "616": "CALL (0x00020DC4) (DB)",
        "619": "I7 = DM(0x00030101)",
        "61f": "DM(0x00, I7) = R8",
        "621": "DM(0x03, I7) = R9",
        "623": "DM(0x01, I7) = R10",
        "625": "DM(0x04, I7) = R11",
        "627": "DM(0x02, I7) = R8",
        "62a": "DM(0x05, I7) = R9",
        "632": "I7 = DM(0x00030101)",
        "638": "DM(0x00, I7) = R8",
        "63a": "DM(0x06, I7) = R9",
        "63c": "DM(0x01, I7) = R10",
        "640": "DM(0x02, I7) = R8",
        "643": "DM(0x08, I7) = R9",
        "64b": "I7 = DM(0x00030101)",
        "651": "DM(0x03, I7) = R8",
        "653": "DM(0x06, I7) = R9",
        "655": "DM(0x04, I7) = R10",
        "657": "DM(0x07, I7) = R11",
        "658": "RTS (DB)",
        "65a": "DM(0x00000008, I7) = R9",
        "65b": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2c slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x2c six-input matrix rebuild contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
