#!/usr/bin/env python3
"""Audit the one-word SHARC helper boundary at opcode 0x0d."""

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
        "26d": "IF FLAG0_IN, JUMP",
        "26e": "R0 = DM(I0, M0)",
        "26f": "CALL (0x00020D5D)",
        "270": "RTS",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0d slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x0d one-word helper boundary contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
