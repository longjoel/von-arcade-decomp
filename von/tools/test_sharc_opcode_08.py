#!/usr/bin/env python3
"""Audit the SHARC service-state reset at opcode 0x08."""

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
        "1bf": "R0 = 0x00000000",
        "1c0": "DM(0x00030100) = R0",
        "1c1": "RTS (DB)",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"opcode 0x08 slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x08 service-state reset contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
