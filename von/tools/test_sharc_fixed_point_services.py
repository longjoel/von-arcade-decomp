#!/usr/bin/env python3
"""Audit the signed fixed-point SHARC service entry shapes."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def load_listing() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            result[slot] = body
    return result


def require(lines: dict[str, str], slot: str, fragment: str) -> None:
    if fragment not in lines.get(slot, ""):
        raise SystemExit(f"SHARC fixed-point service slot {slot} missing {fragment}")


def main() -> int:
    lines = load_listing()

    # Opcode 0x1b -> 0x203b6: one signed 16-bit operand.
    require(lines, "3b7", "R0 = DM(I0, M0)")
    require(lines, "3b8", "R0 = LSHIFT R0 BY 16")
    require(lines, "3b9", "R0 = ASHIFT R0 BY -16")
    require(lines, "3ba", "F0 = FLOAT R0")
    require(lines, "3bb", "CALL (0x00020DC4) (DB)")
    require(lines, "3bc", "R1 = 0x38C9116D")
    require(lines, "3c0", "DM(I1, M0) = R0")

    # Opcode 0x1c -> 0x203c2: same one-operand shape with the sibling helper.
    require(lines, "3c3", "R0 = DM(I0, M0)")
    require(lines, "3c4", "R0 = LSHIFT R0 BY 16")
    require(lines, "3c5", "R0 = ASHIFT R0 BY -16")
    require(lines, "3c6", "F0 = FLOAT R0")
    require(lines, "3c7", "CALL (0x00020DBE) (DB)")
    require(lines, "3c8", "R1 = 0x38C9116D")
    require(lines, "3cc", "DM(I1, M0) = R0")

    # Opcode 0x1d -> 0x203ce: one signed 16-bit angle and one raw F15 value.
    require(lines, "3cf", "R0 = DM(I0, M0)")
    require(lines, "3d0", "IF FLAG0_IN")
    require(lines, "3d1", "R15 = DM(I0, M0)")
    require(lines, "3d2", "R0 = LSHIFT R0 BY 16")
    require(lines, "3d3", "R0 = ASHIFT R0 BY -16")
    require(lines, "3da", "F0 = F0 * F15")
    require(lines, "3db", "DM(I1, M0) = R0")
    require(lines, "3d5", "CALL (0x00020DC4) (DB)")
    require(lines, "3d6", "R1 = 0x38C9116D")

    require(lines, "dbe", "I7 = 0x0003030C")
    require(lines, "dbf", "F8 = ABS F0")
    require(lines, "dc0", "R2 = 0x3FC90FDB")
    require(lines, "dc4", "I7 = 0x0003030C")
    require(lines, "dc5", "R7 = 0x3F800000")
    require(lines, "dc6", "R12 = 0x00000000")
    require(lines, "dd7", "LCNTR = 0x0006, DO (0x00000DD9) UNTIL LCE")

    print("PASS: SHARC 0x1b/0x1c one-input and 0x1d angle-times-float shapes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
