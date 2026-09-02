#!/usr/bin/env python3
"""Audit the five-word SHARC upload service at opcode 0x26."""

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

    for slot, register in zip(("533", "535", "537", "539", "53b"), ("R0", "R1", "R2", "R3", "R4")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x26 slot {slot} missing {register} FIFO read")
    for slot in ("532", "534", "536", "538", "53a"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x26 slot {slot} missing FIFO wait")

    checks = {
        "53c": "I6 = 0x0003013C",
        "53d": "DM(I6, M1) = R0",
        "53e": "DM(I6, M1) = R1",
        "53f": "DM(I6, M1) = R2",
        "540": "RTS (DB)",
        "541": "DM(I6, M1) = R3",
        "542": "DM(I6, M1) = R4",
        "543": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x26 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x26 five-word upload contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
