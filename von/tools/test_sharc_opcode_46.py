#!/usr/bin/env python3
"""Audit the seven-word SHARC state-window upload at opcode 0x46."""

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

    for slot, register in zip(("bcf", "bd1", "bd3", "bd5", "bd7", "bd9", "bdb"), ("R0", "R1", "R2", "R3", "R4", "R5", "R6")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x46 slot {slot} missing {register} FIFO read")
    for slot in ("bce", "bd0", "bd2", "bd4", "bd6", "bd8", "bda"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x46 slot {slot} missing FIFO wait")

    checks = {
        "bdc": "I6 = 0x00030150",
        "bdd": "F4 = -F4,  DM(I6, M1) = R0",
        "bde": "DM(I6, M1) = R1",
        "bdf": "DM(I6, M1) = R2",
        "be0": "DM(I6, M1) = R3",
        "be1": "DM(I6, M1) = R4",
        "be2": "RTS (DB)",
        "be3": "DM(I6, M1) = R5",
        "be4": "DM(I6, M1) = R6",
        "be5": "I6 = 0x00030150",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x46 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x46 seven-word state-upload contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
