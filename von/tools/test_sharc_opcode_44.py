#!/usr/bin/env python3
"""Audit the constant-table initialization service at SHARC opcode 0x44."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    expected = {
        "ba1": "I6 = 0x00030150",
        "ba3": "DM(0x0000000C, I6) = R0",
        "ba5": "DM(0x0000000D, I6) = R0",
        "ba7": "DM(0x0000000E, I6) = R0",
        "baa": "DM(0x0000000F, I6) = R0",
    }
    for slot, fragment in expected.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"opcode 0x44 slot {slot} missing {fragment}")

    constants = {
        "ba2": "R0 = 0x40000000",
        "ba4": "R0 = 0x3EAAAAAB",
        "ba6": "R0 = 0x3F000000",
        "ba9": "R0 = 0x40400000",
    }
    for slot, fragment in constants.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"opcode 0x44 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x44 four-constant initialization contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
