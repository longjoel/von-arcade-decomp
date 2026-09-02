#!/usr/bin/env python3
"""Audit the three-input SHARC normalized threshold predicate at opcode 0x27."""

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

    for slot, register in zip(("544", "546", "548"), ("R12", "R13", "R14")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x27 slot {slot} missing {register} FIFO read")
    for slot in ("543", "545", "547"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x27 slot {slot} missing FIFO wait")

    checks = {
        "549": "I6 = 0x0003013C",
        "54a": "R8 = DM(0x00000000, I6)",
        "550": "R9 = DM(0x00000003, I6)",
        "54b": "F0 = F8 - F12",
        "54c": "F2 = F8 - F14",
        "54f": "F8 = F8 + F15",
        "551": "F4 = RSQRTS F8",
        "55e": "F8 = F8 * F4",
        "55f": "COMP(F8, F9)",
        "560": "IF GT, JUMP (0x0002056A)",
        "561": "F0 = F0 * F4",
        "563": "DM(I1, M0) = R0",
        "565": "DM(I1, M0) = R2",
        "567": "RTS (DB)",
        "568": "DM(I1, M0) = 0x00000001",
        "56a": "IF FLAG1_IN, JUMP",
        "56b": "DM(I1, M0) = 0x00000000",
        "56c": "IF FLAG1_IN, JUMP",
        "56d": "DM(I1, M0) = 0x00000000",
        "56e": "IF FLAG1_IN, JUMP",
        "56f": "RTS (DB)",
        "570": "DM(I1, M0) = 0x00000000",
        "572": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x27 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x27 normalized threshold predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
