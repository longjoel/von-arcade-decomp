#!/usr/bin/env python3
"""Audit the branched normalized predicate at opcode 0x4a."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def predicate(vector: tuple[float, float, float], state: tuple[float, ...], threshold: float) -> int:
    y_difference = vector[1] - state[1]
    if y_difference > 0.0:
        return 1
    distance = math.sqrt(sum((value - state[index]) ** 2 for index, value in enumerate(vector)))
    return 0 if distance < state[3] + threshold else 1


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("c48", "c4b", "c4e", "c52"), ("R8", "R9", "R10", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4a slot {slot} missing {register} FIFO read")
    for slot in ("c47", "c4a", "c4d", "c51"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4a slot {slot} missing FIFO wait")

    checks = {
        "c46": "I6 = 0x00030157",
        "c49": "R12 = DM(0x00000000, I6)",
        "c4c": "R13 = DM(0x01, I6)",
        "c4f": "R14 = DM(0x02, I6)",
        "c50": "IF GT, JUMP (0x00020C6A)",
        "c56": "F4 = RSQRTS F0",
        "c63": "F0 = F0 * F4",
        "c64": "COMP(F0, F11)",
        "c65": "IF LT, JUMP (0x00020C70)",
        "c66": "IF FLAG1_IN, JUMP",
        "c67": "RTS (DB)",
        "c68": "R0 = 0x00000001",
        "c69": "DM(I1, M0) = R0",
        "c6a": "IF FLAG0_IN, JUMP",
        "c6b": "R0 = DM(I0, M0)",
        "c6c": "IF FLAG1_IN, JUMP",
        "c6d": "RTS (DB)",
        "c6e": "R0 = 0x00000001",
        "c6f": "DM(I1, M0) = R0",
        "c70": "IF FLAG1_IN, JUMP",
        "c71": "RTS (DB)",
        "c72": "R0 = 0x00000000",
        "c73": "DM(I1, M0) = R0",
        "c74": "I6 = 0x00030157",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4a slot {slot} missing {fragment}")

    state = (0.0, 0.0, 0.0, 4.0, 5.0)
    if predicate((3.0, 4.0, 0.0), state, 0.0) != 1:
        raise SystemExit("SHARC opcode-0x4a positive-y fallback should return 1")
    if predicate((1.0, -2.0, 2.0), state, 0.0) != 0:
        raise SystemExit("SHARC opcode-0x4a negative-y inside vector should return 0")

    print("PASS: SHARC opcode-0x4a branched normalized predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
