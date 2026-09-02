#!/usr/bin/env python3
"""Audit the no-input SHARC constant-success status service at opcode 0x2b."""

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
        "5f0": "IF FLAG1_IN, JUMP (0x000005F0)",
        "5f1": "RTS (DB)",
        "5f2": "DM(I1, M0) = 0x00000001",
        "5f3": "NOP",
        "5f4": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2b slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x2b constant-success status contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
