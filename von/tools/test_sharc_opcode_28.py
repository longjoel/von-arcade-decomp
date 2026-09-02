#!/usr/bin/env python3
"""Audit the five-input SHARC projected threshold predicate at opcode 0x28."""

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

    for slot, register in zip(("573", "575", "577", "579", "57b"), ("R0", "R1", "R2", "R5", "R6")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x28 slot {slot} missing {register} FIFO read")
    for slot in ("572", "574", "576", "578", "57a"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x28 slot {slot} missing FIFO wait")

    checks = {
        "57c": "I7 = DM(0x00030101)",
        "57d": "R8 = DM(0x00000009, I7)",
        "57e": "R9 = DM(0x0000000A, I7)",
        "57f": "R10 = DM(0x0000000B, I7)",
        "580": "R4 = DM(0x00000000, I7)",
        "581": "F12 = F0 * F4",
        "583": "F12 = F2 * F4",
        "587": "F12 = F0 * F4",
        "589": "R0 = R8",
        "58a": "F2 = F10 + F12",
        "58b": "IF LE, JUMP (0x000205A5)",
        "58d": "IF GE, JUMP (0x000205A5)",
        "58f": "F12 = F2 * F4",
        "590": "F5 = F2 * F5",
        "591": "F4 = RSQRTS F8",
        "59e": "F8 = F8 * F4",
        "59f": "COMP(F8, F5)",
        "5a0": "IF GE, JUMP (0x000205A5)",
        "5a1": "IF FLAG1_IN, JUMP",
        "5a2": "RTS (DB)",
        "5a3": "DM(I1, M0) = 0x00000001",
        "5a5": "IF FLAG1_IN, JUMP",
        "5a6": "RTS (DB)",
        "5a7": "DM(I1, M0) = 0x00000000",
        "5a9": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x28 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x28 projected threshold predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
