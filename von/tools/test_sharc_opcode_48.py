#!/usr/bin/env python3
"""Audit the five-word state-window upload at opcode 0x48."""

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

    for slot, register in zip(("c0f", "c11", "c13", "c15", "c17"), ("R0", "R1", "R2", "R3", "R4")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x48 slot {slot} missing {register} FIFO read")
    for slot in ("c0e", "c10", "c12", "c14", "c16"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x48 slot {slot} missing FIFO wait")

    checks = {
        "c18": "I6 = 0x00030157",
        "c19": "DM(I6, M1) = R0",
        "c1a": "DM(I6, M1) = R1",
        "c1b": "DM(I6, M1) = R2",
        "c1c": "RTS (DB)",
        "c1d": "DM(I6, M1) = R3",
        "c1e": "DM(I6, M1) = R4",
        "c1f": "I6 = 0x00030157",
        "c20": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x48 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x48 five-word state-upload contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
