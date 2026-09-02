#!/usr/bin/env python3
"""Audit the two entry paths into the shared fixed-point reduction helper."""

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

    checks = {
        "dbe": "I7 = 0x0003030C",
        "dbf": "F8 = ABS F0",
        "dc0": "R2 = 0x3FC90FDB",
        "dc1": "JUMP (0x00020DCA) (DB)",
        "dc4": "I7 = 0x0003030C",
        "dc5": "R7 = 0x3F800000",
        "dc6": "R12 = 0x00000000",
        "dc7": "F8 = ABS F0",
        "dc2": "R2 = DM(I7, 0x01)",
        "dc8": "F0 = PASS F0,  R4 = R8",
        "dcb": "R2 = FIX F4",
        "dcc": "BTST R2 BY 0",
        "dd5": "IF LT, JUMP (0x00020DDE)",
        "dd7": "LCNTR = 0x0006, DO (0x00000DD9) UNTIL LCE",
        "ddb": "RTS (DB), F4 = F4 * F8",
        "ddd": "F0 = F12 * F7",
        "dde": "RTS (DB)",
        "ddf": "F0 = F12 * F7",
        "de1": "DM(0x00030109) = R8",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20dbe slot {slot} missing {fragment}")

    common_path = {
        "dca": "F4 = F4 * F2",
        "dcb": "R2 = FIX F4",
        "dcc": "BTST R2 BY 0",
        "dcd": "IF NOT SZ, F7 = -F7",
        "dce": "F4 = FLOAT R2",
        "dcf": "F4 = F4 - F12",
        "dd0": "F12 = F2 * F4",
        "dd1": "F2 = F2 * F4,  F12 = F8 - F12",
        "dd2": "F8 = F12 - F2",
        "dd3": "F12 = ABS F8",
        "dd4": "F12 - F4",
        "dd5": "IF LT, JUMP (0x00020DDE)",
        "dd6": "F12 = F12 * F12",
        "dd8": "F4 = F12 * F4",
        "dd9": "F4 = F2 + F4",
        "dda": "F4 = F12 * F4",
        "ddb": "F4 = F4 * F8",
        "ddc": "F12 = F4 + F8",
        "ddd": "F0 = F12 * F7",
        "ddf": "F0 = F12 * F7",
    }
    for slot, fragment in common_path.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC shared reduction slot {slot} missing {fragment}")

    print("PASS: SHARC helpers 0x20dbe/0x20dc4 shared reduction contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
