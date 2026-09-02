#!/usr/bin/env python3
"""Audit the six-input SHARC vector-length service at opcode 0x1f."""

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

    inputs = {
        "3eb": "R8 = DM(I0, M0)",
        "3ed": "R12 = DM(I0, M0)",
        "3ef": "R9 = DM(I0, M0)",
        "3f1": "R13 = DM(I0, M0)",
        "3f3": "R10 = DM(I0, M0)",
        "3f5": "R14 = DM(I0, M0)",
    }
    for slot, fragment in inputs.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x1f slot {slot} missing {fragment}")
    for slot in ("3ea", "3ec", "3ee", "3f0", "3f2", "3f4"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x1f slot {slot} missing FIFO wait")

    checks = {
        "3ef": "F0 = F8 - F12",
        "3f5": "F4 = PASS F1",
        "3f3": "F8 = F0 * F4",
        "3f6": "F2 = F10 - F14",
        "3f7": "F8 = F8 + F12",
        "3f8": "F12 = F2 * F4",
        "3f9": "F0 = F8 + F12",
        "3fa": "F4 = RSQRTS F0",
        "3fb": "F12 = F4 * F4",
        "3fc": "F12 = F12 * F0",
        "407": "RTS (DB)",
        "408": "F0 = F0 * F4",
        "409": "DM(I1, M0) = R0",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x1f slot {slot} missing {fragment}")
    for slot in ("3fa", "3fb", "3fc", "3ff", "400", "401", "403", "404", "405", "407"):
        if "F" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x1f slot {slot} missing reciprocal-square-root refinement")

    print("PASS: SHARC opcode-0x1f six-input vector-length contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
