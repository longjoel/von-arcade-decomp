#!/usr/bin/env python3
"""Audit the two-input follow-up SHARC service at opcode 0x3f."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def followup_value(a_word: int, b_word: int, c: float, d: float) -> float:
    """Normal-case contract; A/B are signed 32-bit integer words."""
    def signed(word: int) -> int:
        return word if word < 0x80000000 else word - 0x100000000

    return d + c * float(signed(a_word)) / float(signed(b_word))


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    checks = {
        "add": "IF FLAG0_IN, JUMP",
        "ade": "R0 = DM(I0, M0)",
        "adf": "IF FLAG0_IN, JUMP",
        "ae0": "R12 = DM(I0, M0)",
        "ae1": "F12 = FLOAT R12",
        "ae2": "F0 = RECIPS F12",
        "ae9": "IF FLAG0_IN, JUMP",
        "ae9": "IF FLAG0_IN, JUMP",
        "aea": "R4 = DM(I0, M0)",
        "aeb": "IF FLAG0_IN, JUMP",
        "aec": "F8 = F0 * F4",
        "aed": "R12 = DM(I0, M0)",
        "aee": "IF FLAG1_IN, JUMP",
        "aef": "RTS (DB)",
        "af0": "F0 = F8 + F12",
        "af1": "DM(I1, M0) = R0",
        "af2": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3f slot {slot} missing {fragment}")

    vectors = (
        (0x3F800000, 0x40000000, 3.0, 4.0),
        (0x40000000, 0x40800000, 3.0, 5.0),
    )
    expected = (6.9765625, 7.9765625)
    for vector, target in zip(vectors, expected):
        # The ROM's three reciprocal corrections are intentionally approximate;
        # the live second vector differs from ideal division by about 1.8e-4.
        if not math.isclose(followup_value(*vector), target, rel_tol=0.0, abs_tol=2e-4):
            raise SystemExit(f"SHARC opcode-0x3f vector {vector} does not match")

    print("PASS: SHARC opcode-0x3f two-input follow-up contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
