#!/usr/bin/env python3
"""Audit the three-input SHARC two-result fixed-point projection at opcode 0x25."""

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

    for slot, register in zip(("50b", "50d", "50f"), ("R1", "R0", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x25 slot {slot} missing {register} FIFO read")
    for slot in ("50a", "50c", "50e"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x25 slot {slot} missing FIFO wait")

    checks = {
        "516": "F4 = RSQRTS F1",
        "517": "R11 = DM(0x00, I3)",
        "522": "CALL (0x00020D68) (DB)",
        "525": "R1 = 0x4622F83D",
        "527": "R0 = FIX F0",
        "528": "IF FLAG1_IN, JUMP",
        "529": "DM(I1, M0) = R0",
        "52a": "CALL (0x00020D68) (DB)",
        "52f": "RTS (DB), F0 = F0 * F1",
        "530": "R0 = FIX F0",
        "531": "DM(I1, M0) = R0",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x25 slot {slot} missing {fragment}")

    if "IF FLAG0_IN, JUMP" not in lines.get("532", ""):
        raise SystemExit("SHARC opcode-0x25 boundary does not reach opcode 0x26")

    print("PASS: SHARC opcode-0x25 two-result fixed-point projection contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
