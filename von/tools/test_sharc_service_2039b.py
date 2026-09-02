#!/usr/bin/env python3
"""Audit the SHARC three-input state-output service at target 0x2039b."""

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
        "39b": "IF FLAG0_IN, JUMP",
        "39c": "R0 = DM(I0, M0)",
        "39d": "IF FLAG0_IN, JUMP",
        "39e": "R1 = DM(I0, M0)",
        "39f": "IF FLAG0_IN, JUMP",
        "3a0": "R2 = DM(I0, M0)",
        "3a1": "I7 = DM(0x00030101)",
        "3a2": "R8 = DM(0x00000009, I7)",
        "3a3": "R9 = DM(0x0000000A, I7)",
        "3a4": "R10 = DM(0x0000000B, I7)",
        "3a5": "R4 = DM(0x00000000, I7)",
        "3a6": "R4 = DM(0x03, I7)",
        "3a7": "R4 = DM(0x06, I7)",
        "3a8": "R4 = DM(0x01, I7)",
        "3a9": "R4 = DM(0x04, I7)",
        "3aa": "R4 = DM(0x07, I7)",
        "3ab": "R4 = DM(0x02, I7)",
        "3ac": "R4 = DM(0x05, I7)",
        "3ad": "R4 = DM(0x08, I7)",
        "3ae": "IF FLAG1_IN, JUMP",
        "3af": "DM(I1, M0) = R8",
        "3b0": "IF FLAG1_IN, JUMP",
        "3b1": "DM(I1, M0) = R9",
        "3b2": "IF FLAG1_IN, JUMP",
        "3b3": "RTS (DB)",
        "3b4": "DM(I1, M0) = R10",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing {fragment}")

    for slot in ("3a6", "3a7", "3a8", "3a9", "3aa", "3ab", "3ac", "3ad"):
        if " * F4" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing coefficient multiply")
    for slot in ("3a6", "3a7", "3a8", "3a9", "3aa", "3ab", "3ac", "3ad", "3af"):
        if "F8 = F8 +" not in lines.get(slot, "") and slot in ("3a7", "3a8", "3a9"):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing X accumulator update")
    for slot in ("3aa", "3ab", "3ac"):
        if "F9 = F9 +" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing Y accumulator update")
    for slot in ("3ad", "3af"):
        if "F10 = F10 +" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing Z accumulator update")
    for slot in ("3af", "3b1", "3b4"):
        if "DM(I1, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC target-0x2039b slot {slot} missing output FIFO write")

    print("PASS: SHARC target-0x2039b three-input state-output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
