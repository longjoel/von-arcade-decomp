#!/usr/bin/env python3
"""Audit the four-input normalized predicate at opcode 0x49."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def predicate(vector: tuple[float, float, float], state: tuple[float, ...], threshold: float) -> int:
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

    for slot, register in zip(("c21", "c24", "c27", "c2a"), ("R8", "R9", "R10", "R15")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x49 slot {slot} missing {register} FIFO read")
    for slot in ("c20", "c23", "c26", "c29"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x49 slot {slot} missing FIFO wait")

    checks = {
        "c1f": "I6 = 0x00030157",
        "c22": "R12 = DM(0x00000000, I6)",
        "c25": "R13 = DM(0x01, I6)",
        "c28": "R14 = DM(0x02, I6)",
        "c2c": "R1 = DM(0x07, I6)",
        "c2d": "R8 = DM(0x08, I6)",
        "c2e": "F4 = RSQRTS F0",
        "c3b": "F0 = F0 * F4",
        "c3c": "COMP(F0, F9)",
        "c3d": "IF LT, JUMP (0x00020C42)",
        "c3e": "IF FLAG1_IN, JUMP",
        "c3f": "RTS (DB)",
        "c40": "R0 = 0x00000001",
        "c41": "DM(I1, M0) = R0",
        "c42": "IF FLAG1_IN, JUMP",
        "c43": "RTS (DB)",
        "c44": "R0 = 0x00000000",
        "c45": "DM(I1, M0) = R0",
        "c46": "I6 = 0x00030157",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x49 slot {slot} missing {fragment}")

    if "R9 = DM(0x03, I6)" not in lines.get("c2e", ""):
        raise SystemExit("SHARC opcode-0x49 slot c2e missing state bound load")
    state = (0.0, 0.0, 0.0, 4.0, 5.0)
    if predicate((3.0, 4.0, 0.0), state, 0.0) != 1:
        raise SystemExit("SHARC opcode-0x49 outside vector should return 1")
    if predicate((1.0, 2.0, 2.0), state, 0.0) != 0:
        raise SystemExit("SHARC opcode-0x49 inside vector should return 0")

    print("PASS: SHARC opcode-0x49 normalized predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
