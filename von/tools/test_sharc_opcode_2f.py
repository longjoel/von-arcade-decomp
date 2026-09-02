#!/usr/bin/env python3
"""Audit the packed-vector SHARC translation-tail update at opcode 0x2f."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def project_row_vector(vector: tuple[float, float, float],
                       matrix: tuple[float, ...]) -> tuple[float, float, float]:
    """Model opcode 0x2f's matrix-to-tail coefficient order."""
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

    for slot, register in zip(("6e2", "6e4", "6e6"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2f slot {slot} missing {register} FIFO read")
    for slot in ("6e1", "6e3", "6e5"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2f slot {slot} missing FIFO wait")

    checks = {
        "6e7": "I7 = DM(0x00030101)",
        "6e8": "I6 = 0x00030141",
        "6eb": "R8 = DM(0x00000000, I6)",
        "6ec": "R6 = R6 AND R8",
        "6ed": "R0 = R5 AND R7",
        "6f2": "R0 = R0 OR R6",
        "6f5": "R6 = R6 AND R8",
        "6fa": "R10 = DM(0x0B, I7)",
        "6fb": "R9 = DM(0x0A, I7)",
        "6fe": "R6 = R6 AND R8",
        "703": "R8 = DM(0x09, I7)",
        "70d": "DM(0x09, I7) = R8",
        "70e": "RTS (DB)",
        "70f": "DM(0x0A, I7) = R9",
        "710": "DM(0x0000000B, I7) = R10",
        "711": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2f slot {slot} missing {fragment}")

    coefficient_groups = {
        "705": "F12 = F0 * F4",
        "706": "F8 = F8 + F12",
        "707": "F9 = F9 + F12",
        "708": "F10 = F10 + F12",
        "709": "F8 = F8 + F12",
        "70a": "F9 = F9 + F12",
        "70b": "F10 = F10 + F12",
        "70c": "F8 = F8 + F12",
        "70d": "F9 = F9 + F12",
    }
    for slot, fragment in coefficient_groups.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2f slot {slot} missing {fragment}")
    if project_row_vector((1.0, 2.0, 3.0),
                         (0.0, -1.0, 0.0, 1.0, 0.0, 0.0,
                          0.0, 0.0, 1.0)) != (2.0, -1.0, 3.0):
        raise SystemExit("SHARC opcode-0x2f matrix coefficient order mismatch")

    print("PASS: SHARC opcode-0x2f packed-vector tail update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
