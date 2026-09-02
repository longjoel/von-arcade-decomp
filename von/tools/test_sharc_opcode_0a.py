#!/usr/bin/env python3
"""Audit the two-input scalar SHARC service at opcode 0x0a."""

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

    checks = {
        "211": "IF FLAG0_IN, JUMP",
        "212": "R1 = DM(I0, M0)",
        "213": "IF FLAG0_IN, JUMP",
        "214": "CALL (0x00020D68) (DB)",
        "215": "R0 = DM(I0, M0)",
        "216": "R3 = 0x4622F83D",
        "217": "IF FLAG1_IN, JUMP",
        "218": "RTS (DB), F0 = F0 * F3",
        "219": "R0 = FIX F0",
        "21a": "DM(I1, M0) = R0",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0a slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x0a delayed-R0/R1 helper, fixed-scale, and output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
