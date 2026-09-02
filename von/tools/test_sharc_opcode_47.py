#!/usr/bin/env python3
"""Audit the four-input normalized predicate at opcode 0x47."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def predicate_result(a: float, b: float, c: float, d: float,
                    state: tuple[float, ...]) -> int:
    """Model opcode 0x47's normal-case delayed binary result."""
    radial = math.sqrt((a - state[0]) ** 2 + (b - state[2]) ** 2)
    delta = state[1] - d
    inside = (c + state[5] > radial and
              state[4] <= delta <= state[3])
    return 0 if inside else 1


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("be7", "bea", "bed", "bf2"), ("R8", "R10", "R9", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x47 slot {slot} missing {register} FIFO read")
    for slot in ("be6", "be9", "bec", "bf1"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x47 slot {slot} missing FIFO wait")

    checks = {
        "be5": "I6 = 0x00030150",
        "be8": "R12 = DM(0x00000000, I6)",
        "beb": "R14 = DM(0x02, I6)",
        "bee": "R13 = DM(0x05, I6)",
        "bef": "R1 = DM(0x0E, I6)",
        "bf0": "R8 = DM(0x0F, I6)",
        "bf2": "F4 = RSQRTS F0",
        "bff": "F0 = F0 * F4",
        "c00": "COMP(F2, F0)",
        "c01": "IF LE, JUMP (0x00020C0A)",
        "c02": "COMP(F1, F14)",
        "c03": "IF GT, JUMP (0x00020C0A)",
        "c04": "COMP(F1, F15)",
        "c05": "IF LT, JUMP (0x00020C0A)",
        "c06": "IF FLAG1_IN, JUMP",
        "c07": "RTS (DB)",
        "c08": "R0 = 0x00000000",
        "c09": "DM(I1, M0) = R0",
        "c0a": "IF FLAG1_IN, JUMP",
        "c0b": "RTS (DB)",
        "c0c": "R0 = 0x00000001",
        "c0d": "DM(I1, M0) = R0",
        "c0e": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x47 slot {slot} missing {fragment}")

    state = (0.0, 0.0, 0.0, 3.0, -0.5, 0.0, 0.0)
    vectors = {
        (3.0, 4.0, 6.0, -2.0): 0,       # inside, inclusive interval
        (3.0, 4.0, 5.0, -2.0): 1,       # radial inequality is strict
        (3.0, 4.0, 6.0, 0.5): 0,       # delta == stored lower bound
        (3.0, 4.0, 6.0, -3.0): 0,      # delta == upper bound
        (3.0, 4.0, 6.0, 0.5001): 1,   # below lower bound
        (3.0, 4.0, 6.0, -3.0001): 1,  # above upper bound
    }
    for vector, expected in vectors.items():
        actual = predicate_result(*vector, state)
        if actual != expected:
            raise SystemExit(
                f"SHARC opcode-0x47 predicate {vector}: "
                f"expected {expected}, got {actual}"
            )

    print("PASS: SHARC opcode-0x47 normalized predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
