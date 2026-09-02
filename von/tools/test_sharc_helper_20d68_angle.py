#!/usr/bin/env python3
"""Audit the angle-reduction constants and caller contract for SHARC 0x20d68."""

from __future__ import annotations

import math
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def f32(word: int) -> float:
    return struct.unpack(">f", word.to_bytes(4, "big"))[0]


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" in line:
            slot, body = line.split(":", 1)
            if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
                lines[slot] = body

    # DM 0x30300 is the helper's range-reduction/atan approximation table.
    words = []
    for slot in ("0e8", "0e9", "0ea", "0eb", "0ec", "0ed", "0ee"):
        body = lines.get(slot, "")
        marker = "DM(I0, M0) = 0x"
        if marker not in body:
            raise SystemExit(f"SHARC angle table slot {slot} missing constant")
        words.append(int(body.split(marker, 1)[1].split()[0], 16))
    if words[:2] != [0x3E8930A3, 0x3FDDB3D7]:
        raise SystemExit("SHARC angle table lost its 2-sqrt(3), sqrt(3) anchors")
    if not math.isclose(f32(words[0]), 2.0 - math.sqrt(3.0), rel_tol=0, abs_tol=2e-7):
        raise SystemExit("DM 0x30300[0] is not 2-sqrt(3)")
    if not math.isclose(f32(words[1]), math.sqrt(3.0), rel_tol=0, abs_tol=2e-7):
        raise SystemExit("DM 0x30300[1] is not sqrt(3)")

    # Opcode 0x0f subtracts endpoint pairs, then converts the angle result to
    # signed fixed-point with the same pi/32767 scale used by 0x1b/0x1c.
    required = {
        "285": "F1 = F1 - F3",
        "286": "F0 = F0 - F2",
        "287": "CALL (0x00020D68)",
        "288": "R1 = 0x4622F83D",
        "28a": "R0 = FIX F0",
    }
    for slot, fragment in required.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC angle caller slot {slot} missing {fragment}")

    print("PASS: SHARC 0x20d68 angle-reduction constants and difference-vector caller")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
