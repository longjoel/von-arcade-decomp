#!/usr/bin/env python3
"""Audit the statically recovered SHARC opcode-0x18 state-window service."""

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

    required = {
        "e54": "IF FLAG0_IN, JUMP",
        "e55": "R0 = DM(I0, M0)",
        "e56": "R0 = LSHIFT R0 BY 4",
        "e58": "I7 = DM(0x00030104)",
        "e5a": "I6 = 0x0003010B",
        "e5b": "LCNTR = 0x0010",
        "38e": "CALL (0x00020E54)",
        "38f": "I7 = 0x0003010B",
        "390": "LCNTR = 0x000C",
        "395": "DM(I1, M0) = R0",
    }
    for slot, fragment in required.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x18 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x18 one-input state-window/12-word-output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
