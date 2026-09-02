#!/usr/bin/env python3
"""Audit the three-input, three-result matrix projection at opcode 0x43."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def project(vector: tuple[float, float, float], matrix: tuple[float, ...]) -> tuple[float, float, float]:
    x, y, z = vector
    return (
        x * matrix[0] + y * matrix[3] + z * matrix[6],
        x * matrix[1] + y * matrix[4] + z * matrix[7],
        x * matrix[2] + y * matrix[5] + z * matrix[8],
    )


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("b8a", "b8c", "b8e"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x43 slot {slot} missing {register} FIFO read")
    for slot in ("b89", "b8b", "b8d"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x43 slot {slot} missing FIFO wait")

    checks = {
        "b8f": "I7 = DM(0x00030101)",
        "b90": "R4 = DM(0x00000000, I7)",
        "b91": "F8 = F0 * F4",
        "b93": "F8 = F8 + F12",
        "b94": "F9 = F0 * F4",
        "b97": "F10 = F0 * F4",
        "b99": "IF FLAG1_IN, JUMP",
        "b9a": "DM(I1, M0) = R8",
        "b9b": "IF FLAG1_IN, JUMP",
        "b9c": "DM(I1, M0) = R9",
        "b9d": "IF FLAG1_IN, JUMP",
        "b9e": "RTS (DB)",
        "b9f": "DM(I1, M0) = R10",
        "ba1": "I6 = 0x00030150",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x43 slot {slot} missing {fragment}")

    observed = project((10.0, 20.0, 30.0), tuple(float(value) for value in range(1, 10)))
    if not all(math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-7)
               for actual, expected in zip(observed, (300.0, 360.0, 420.0))):
        raise SystemExit(f"SHARC opcode-0x43 projection mismatch: {observed}")

    print("PASS: SHARC opcode-0x43 three-input projection contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
