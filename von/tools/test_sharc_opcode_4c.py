#!/usr/bin/env python3
"""Audit the branched normalized predicate at opcode 0x4c."""

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

    for slot, register in zip(("ccc", "ccf", "cd2", "cd6"), ("R8", "R9", "R10", "R11")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4c slot {slot} missing {register} FIFO read")
    for slot in ("ccb", "cce", "cd1", "cd5"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4c slot {slot} missing FIFO wait")

    checks = {
        "cca": "I6 = 0x00030157",
        "ccd": "R12 = DM(0x00000000, I6)",
        "cd0": "R13 = DM(0x01, I6)",
        "cd3": "R14 = DM(0x02, I6)",
        "ccf": "F0 = F8 - F12",
        "cd2": "F8 = F0 * F4",
        "cd4": "IF LT, JUMP (0x00020CEE)",
        "cda": "F4 = RSQRTS F0",
        "ce8": "COMP(F0, F11)",
        "ce7": "F0 = F0 * F4",
        "ce8": "COMP(F0, F11)",
        "ce9": "IF LT, JUMP (0x00020CF4)",
        "cea": "IF FLAG1_IN, JUMP",
        "ceb": "RTS (DB)",
        "cec": "R0 = 0x00000001",
        "ced": "DM(I1, M0) = R0",
        "cee": "IF FLAG0_IN, JUMP",
        "cef": "R0 = DM(I0, M0)",
        "cf0": "IF FLAG1_IN, JUMP",
        "cf1": "RTS (DB)",
        "cf2": "R0 = 0x00000001",
        "cf3": "DM(I1, M0) = R0",
        "cf4": "IF FLAG1_IN, JUMP",
        "cf5": "RTS (DB)",
        "cf6": "R0 = 0x00000000",
        "cf7": "DM(I1, M0) = R0",
        "cf8": "I6 = 0x00030157",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4c slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x4c branched normalized predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
