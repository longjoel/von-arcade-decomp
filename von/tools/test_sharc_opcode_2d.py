#!/usr/bin/env python3
"""Audit the one-word SHARC passthrough service at opcode 0x2d."""

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
        "65b": "IF FLAG0_IN, JUMP (0x0000065B)",
        "65c": "R0 = DM(I0, M0)",
        "65d": "IF FLAG1_IN, JUMP (0x0000065D)",
        "65e": "RTS (DB)",
        "65f": "DM(I1, M0) = R0",
        "660": "NOP",
        "661": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x2d slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x2d one-word passthrough contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
