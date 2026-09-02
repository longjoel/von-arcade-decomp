#!/usr/bin/env python3
"""Audit the table-copy/output service at opcode 0x3a."""

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
        "9ac": "IF FLAG0_IN, JUMP",
        "9ad": "R0 = DM(I0, M0)",
        "9ae": "R1 = 0x01400000",
        "9af": "R0 = LSHIFT R0 BY -2",
        "9b0": "R0 = R0 + R1",
        "9b1": "I6 = DM(0x00030101)",
        "9b2": "I7 = R0",
        "9b3": "R0 = 0x05800B0B",
        "9b4": "DM(I7, M1) = R0",
        "9b5": "R0 = DM(I6, M1)",
        "9cc": "IF FLAG1_IN, JUMP",
        "9cd": "RTS (DB)",
        "9ce": "DM(I1, M0) = R0",
        "9cf": "DM(I7, M1) = R0",
        "9d0": "I7 = 0x01407FFF",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3a slot {slot} missing {fragment}")

    stores = sum("DM(I7, M1) = R0" in lines.get(f"{slot:03x}", "") for slot in range(0x9b4, 0x9d0))
    reads = sum("R0 = DM(I6, M1)" in lines.get(f"{slot:03x}", "") for slot in range(0x9b4, 0x9d0))
    if stores != 13 or reads != 12:
        raise SystemExit(f"SHARC opcode-0x3a expected 13 stores/12 reads, got {stores}/{reads}")

    print("PASS: SHARC opcode-0x3a table-copy/output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
