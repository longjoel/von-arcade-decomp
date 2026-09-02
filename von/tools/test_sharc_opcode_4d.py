#!/usr/bin/env python3
"""Audit the extended three-valued predicate at opcode 0x4d."""

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

    for slot, register in zip(("cfa", "cfd", "d00", "d04"), ("R8", "R9", "R10", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4d slot {slot} missing {register} FIFO read")
    for slot in ("cf9", "cfc", "cff", "d03"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4d slot {slot} missing FIFO wait")

    checks = {
        "cf8": "I6 = 0x00030157",
        "cfb": "R12 = DM(0x00000000, I6)",
        "cfe": "R13 = DM(0x01, I6)",
        "d01": "R14 = DM(0x02, I6)",
        "d02": "IF LT, JUMP (0x00020D48)",
        "d08": "F4 = RSQRTS F1",
        "d14": "CALL (0x00020D68)",
        "d15": "F4 = F4 * F12",
        "d16": "F1 = F1 * F4",
        "d17": "CALL (0x00020DBE)",
        "d18": "F1 = PASS F14",
        "d19": "F15 = F1 * F4",
        "d1a": "CALL (0x00020DC4)",
        "d1b": "F15 = F9 + F15",
        "d22": "F4 = RSQRTS F0",
        "d30": "F4 = RSQRTS F15",
        "d3e": "COMP(F0, F1)",
        "d3f": "IF LT, JUMP (0x00020D44)",
        "d40": "IF FLAG1_IN, JUMP",
        "d41": "RTS (DB)",
        "d42": "R0 = 0x00000002",
        "d43": "DM(I1, M0) = R0",
        "d44": "IF FLAG1_IN, JUMP",
        "d45": "RTS (DB)",
        "d46": "R0 = 0x00000000",
        "d47": "DM(I1, M0) = R0",
        "d48": "IF FLAG0_IN, JUMP",
        "d49": "R0 = DM(I0, M0)",
        "d4a": "IF FLAG1_IN, JUMP",
        "d4b": "RTS (DB)",
        "d4c": "R0 = 0x00000001",
        "d4d": "DM(I1, M0) = R0",
        "d4e": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4d slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x4d extended three-valued predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
