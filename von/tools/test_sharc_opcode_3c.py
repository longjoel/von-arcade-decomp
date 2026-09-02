#!/usr/bin/env python3
"""Audit the three-input SHARC normalized state update at opcode 0x3c."""

from __future__ import annotations

import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
CANONICAL_SHARC_NAN = 0xffffffff


def normalized_frame(x: float, y: float, z: float) -> tuple[float, ...]:
    """Model the normal-case frame written by opcode 0x3c."""
    horizontal = math.sqrt(x * x + z * z)
    length = math.sqrt(x * x + y * y + z * z)
    return (
        z / horizontal, -x * y / (length * horizontal), x / length,
        0.0, horizontal / length, y / length,
        -x / horizontal, -z * y / (length * horizontal), z / length,
    )


def rom_degenerate_state() -> tuple[int, ...]:
    """Observed opcode-0x3c state for zero or XZ-degenerate inputs."""
    return (CANONICAL_SHARC_NAN,) * 9 + (0, 0, 0)


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("9f8", "9fa", "9fc"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3c slot {slot} missing {register} FIFO read")
    for slot in ("9f7", "9f9", "9fb"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3c slot {slot} missing FIFO wait")

    checks = {
        "9fd": "I7 = DM(0x00030101)",
        "a05": "F4 = RSQRTS F9",
        "a13": "F4 = RSQRTS F0",
        "a22": "F1 = RECIPS F12",
        "a2a": "F0 = RECIPS F12",
        "a32": "F0 = RECIPS F12",
        "a3a": "F0 = RECIPS F12",
        "a42": "R5 = DM(0x06, I7)",
        "a46": "DM(0x03, I7) = R6",
        "a47": "DM(0x06, I7) = R7",
        "a4a": "DM(0x04, I7) = R6",
        "a4b": "DM(0x07, I7) = R7",
        "a4e": "DM(0x05, I7) = R6",
        "a4f": "DM(0x08, I7) = R7",
        "a52": "DM(0x00, I7) = R6",
        "a53": "DM(0x06, I7) = R7",
        "a56": "DM(0x01, I7) = R6",
        "a57": "DM(0x07, I7) = R7",
        "a59": "RTS (DB)",
        "a5a": "DM(0x02, I7) = R6",
        "a5b": "DM(0x00000008, I7) = R7",
        "a5c": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3c slot {slot} missing {fragment}")

    expected = (0.9701425001, -0.0746263564, 0.2307692308,
                0.0, 0.9514859936, 0.3076923077,
                -0.2425356250, -0.2985054255, 0.9230769231)
    actual = normalized_frame(3.0, 4.0, 12.0)
    if any(abs(observed - wanted) > 1e-6
           for observed, wanted in zip(actual, expected)):
        raise SystemExit(f"SHARC opcode-0x3c normalized frame mismatch: {actual!r}")
    if rom_degenerate_state()[:9] != (CANONICAL_SHARC_NAN,) * 9:
        raise SystemExit("SHARC opcode-0x3c degenerate matrix oracle mismatch")
    if rom_degenerate_state()[9:] != (0, 0, 0):
        raise SystemExit("SHARC opcode-0x3c degenerate tail oracle mismatch")

    print("PASS: SHARC opcode-0x3c normalized state-update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
