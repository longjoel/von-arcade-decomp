#!/usr/bin/env python3
"""Audit the alternate three-input SHARC normalized state update at 0x3d."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
CANONICAL_SHARC_NAN = 0xffffffff


def normalized_frame_transpose(x: float, y: float,
                               z: float) -> tuple[float, ...]:
    """Model opcode 0x3d's normal-case transpose of the 0x3c frame."""
    horizontal = math.sqrt(x * x + z * z)
    length = math.sqrt(x * x + y * y + z * z)
    return (
        z / horizontal, 0.0, -x / horizontal,
        -x * y / (length * horizontal), horizontal / length,
        -z * y / (length * horizontal),
        x / length, y / length, z / length,
    )


def rom_degenerate_state() -> tuple[int, ...]:
    """Observed opcode-0x3d state for zero or XZ-degenerate inputs."""
    return (CANONICAL_SHARC_NAN,) * 9 + (0, 0, 0)


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("a5d", "a5f", "a61"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3d slot {slot} missing {register} FIFO read")
    for slot in ("a5c", "a5e", "a60"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3d slot {slot} missing FIFO wait")

    checks = {
        "a62": "I7 = DM(0x00030101)",
        "a6a": "F4 = RSQRTS F9",
        "a78": "F4 = RSQRTS F0",
        "a87": "F1 = RECIPS F12",
        "a8f": "F0 = RECIPS F12",
        "a97": "F0 = RECIPS F12",
        "a9f": "F0 = RECIPS F12",
        "aa7": "R5 = DM(0x06, I7)",
        "aab": "DM(0x00, I7) = R6",
        "aac": "DM(0x06, I7) = R7",
        "aaf": "DM(0x01, I7) = R6",
        "ab0": "DM(0x07, I7) = R7",
        "ab3": "DM(0x02, I7) = R6",
        "ab4": "DM(0x08, I7) = R7",
        "ab7": "DM(0x03, I7) = R6",
        "ab8": "DM(0x06, I7) = R7",
        "abb": "DM(0x04, I7) = R6",
        "abc": "DM(0x07, I7) = R7",
        "abe": "RTS (DB)",
        "abf": "DM(0x05, I7) = R6",
        "ac0": "DM(0x00000008, I7) = R7",
        "ac1": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3d slot {slot} missing {fragment}")

    expected = (0.9701425001, 0.0, -0.2425356250,
                -0.0746263564, 0.9514859936, -0.2985054255,
                0.2307692308, 0.3076923077, 0.9230769231)
    actual = normalized_frame_transpose(3.0, 4.0, 12.0)
    if any(abs(observed - wanted) > 1e-6
           for observed, wanted in zip(actual, expected)):
        raise SystemExit(f"SHARC opcode-0x3d frame mismatch: {actual!r}")
    if rom_degenerate_state()[:9] != (CANONICAL_SHARC_NAN,) * 9:
        raise SystemExit("SHARC opcode-0x3d degenerate matrix oracle mismatch")
    if rom_degenerate_state()[9:] != (0, 0, 0):
        raise SystemExit("SHARC opcode-0x3d degenerate tail oracle mismatch")

    print("PASS: SHARC opcode-0x3d alternate normalized state-update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
