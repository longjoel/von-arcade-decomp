#!/usr/bin/env python3
"""Audit the nine-input SHARC persistent-matrix rebuild at opcode 0x32."""

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

    for slot, register in zip(("7c9", "7cb", "7cd", "7cf", "7d1", "7d3", "7d5", "7d7", "7d9"), ("R0", "R1", "R2", "R3", "R13", "R14", "R15", "R5", "R6")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x32 slot {slot} missing {register} FIFO read")
    for slot in ("7c8", "7ca", "7cc", "7ce", "7d0", "7d2", "7d4", "7d6", "7d8"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x32 slot {slot} missing FIFO wait")

    checks = {
        "7da": "I7 = DM(0x00030101)",
        "7db": "R8 = DM(0x00000009, I7)",
        "7dd": "R10 = DM(0x0000000B, I7)",
        "7e7": "DM(0x09, I7) = R8",
        "7e8": "DM(0x0A, I7) = R9",
        "7eb": "DM(0x0B, I7) = R10",
        "7ec": "R1 = 0x38C9116D",
        "7ed": "CALL (0x00020DBE) (DB)",
        "7f0": "CALL (0x00020DC4) (DB)",
        "7f3": "I7 = DM(0x00030101)",
        "7f9": "DM(0x00, I7) = R8",
        "7fb": "DM(0x06, I7) = R9",
        "7fd": "DM(0x01, I7) = R10",
        "801": "DM(0x02, I7) = R8",
        "802": "DM(0x00000008, I7) = R9",
        "811": "R0 = LSHIFT R5 BY 16",
        "814": "R1 = 0x38C9116D",
        "815": "CALL (0x00020DBE) (DB)",
        "818": "CALL (0x00020DC4) (DB)",
        "81b": "I7 = DM(0x00030101)",
        "821": "DM(0x00, I7) = R8",
        "823": "DM(0x03, I7) = R9",
        "825": "DM(0x01, I7) = R10",
        "829": "DM(0x02, I7) = R8",
        "82a": "R0 = LSHIFT R6 BY 16",
        "82e": "CALL (0x00020DBE) (DB)",
        "831": "CALL (0x00020DC4) (DB)",
        "834": "I7 = DM(0x00030101)",
        "83a": "DM(0x03, I7) = R8",
        "83c": "DM(0x06, I7) = R9",
        "83e": "DM(0x04, I7) = R10",
        "842": "DM(0x05, I7) = R8",
        "841": "RTS (DB)",
        "843": "DM(0x00000008, I7) = R9",
        "844": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x32 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x32 nine-input matrix rebuild contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
