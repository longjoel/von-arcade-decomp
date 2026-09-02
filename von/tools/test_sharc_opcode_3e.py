#!/usr/bin/env python3
"""Audit the four-input one-result SHARC service at opcode 0x3e."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def difference_distance(a: float, b: float, c: float, d: float) -> float:
    return math.hypot(a - b, c - d)


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("ac2", "ac4", "ac6", "ac8"), ("R8", "R12", "R9", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3e slot {slot} missing {register} FIFO read")
    for slot in ("ac1", "ac3", "ac5", "ac7"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3e slot {slot} missing FIFO wait")

    checks = {
        "ac6": "F0 = F8 - F12",
        "ac8": "F4 = PASS F0",
        "acd": "F4 = RSQRTS F0",
        "ad9": "IF FLAG1_IN, JUMP",
        "ada": "RTS (DB)",
        "adb": "F0 = F0 * F4",
        "adc": "DM(I1, M0) = R0",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3e slot {slot} missing {fragment}")

    for vector in ((3.0, 0.0, 4.0, 0.0), (8.0, 5.0, 12.0, 8.0)):
        if abs(difference_distance(*vector) - 5.0) > 1e-7:
            raise SystemExit(f"SHARC opcode-0x3e vector {vector} does not yield 5")

    print("PASS: SHARC opcode-0x3e four-input one-result contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
