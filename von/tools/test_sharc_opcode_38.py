#!/usr/bin/env python3
"""Audit the packed-vector geometry service at opcode 0x38."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def decode_packed_coordinate(word: int) -> int:
    """Model the exact normal-coordinate bit construction in opcode 0x38."""
    packed = word & 0xffff
    sign = packed & 0x8000
    exponent = (packed >> 10) & 0x1f
    mantissa = packed & 0x03ff
    return ((sign << 16) |
            (((exponent - 15 + 127) & 0xff) << 23) |
            (mantissa << 13)) & 0xffffffff


def project_row_vector(vector: tuple[float, float, float],
                       matrix: tuple[float, ...]) -> tuple[float, float, float]:
    """Model opcode 0x38's row-vector/column-dot-product ordering."""
    return tuple(sum(vector[row] * matrix[row * 3 + column]
                     for row in range(3)) for column in range(3))


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    for slot, register in zip(("957", "959", "95b"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x38 slot {slot} missing {register} FIFO read")
    for slot in ("956", "958", "95a"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x38 slot {slot} missing FIFO wait")

    checks = {
        "95c": "I7 = DM(0x00030101)",
        "95d": "I6 = 0x00030141",
        "95e": "R8 = DM(0x00000000, I6)",
        "961": "R6 = R6 AND R8",
        "967": "R0 = R0 OR R6",
        "96f": "R1 = R1 AND R7",
        "970": "R1 = R1 OR R6",
        "978": "R2 = R2 AND R7",
        "979": "R2 = R2 OR R6",
        "97a": "F12 = F0 * F4",
        "981": "F12 = F2 * F4",
        "982": "IF FLAG1_IN, JUMP",
        "983": "DM(I1, M0) = R8",
        "984": "IF FLAG1_IN, JUMP",
        "985": "DM(I1, M0) = R9",
        "986": "IF FLAG1_IN, JUMP",
        "987": "RTS (DB)",
        "988": "DM(I1, M0) = R10",
        "98a": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x38 slot {slot} missing {fragment}")

    coefficient_groups = {
        "97a": "F12 = F0 * F4",
        "97b": "F8 = F8 + F12",
        "97c": "F9 = F9 + F12",
        "97d": "F10 = F10 + F12",
        "97e": "F8 = F8 + F12",
        "97f": "F9 = F9 + F12",
        "980": "F10 = F10 + F12",
        "981": "F8 = F8 + F12",
        "983": "F9 = F9 + F12",
    }
    for slot, fragment in coefficient_groups.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x38 slot {slot} missing {fragment}")
    if project_row_vector((1.0, 2.0, 3.0),
                         (0.0, -1.0, 0.0, 1.0, 0.0, 0.0,
                          0.0, 0.0, 1.0)) != (2.0, -1.0, 3.0):
        raise SystemExit("SHARC opcode-0x38 matrix coefficient order mismatch")

    # These vectors exercise the table masks without assuming IEEE half
    # special-case behavior that the ROM instruction sequence does not have.
    vectors = {
        0x3c00: 0x3f800000,  # +1.0
        0xbc00: 0xbf800000,  # -1.0
        0x4000: 0x40000000,  # +2.0
        0xc000: 0xc0000000,  # -2.0
    }
    for packed, expected in vectors.items():
        actual = decode_packed_coordinate(packed)
        if actual != expected:
            raise SystemExit(
                f"SHARC opcode-0x38 packed decode {packed:04x}: "
                f"expected {expected:08x}, got {actual:08x}"
            )

    print("PASS: SHARC opcode-0x38 packed-vector geometry contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
