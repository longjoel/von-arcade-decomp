#!/usr/bin/env python3
"""Audit the fixed-source table-copy bridge at opcode 0x3b."""

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
        "9d0": "I7 = 0x01407FFF",
        "9d1": "R0 = DM(0x00000000, I7)",
        "9d2": "IF FLAG1_IN, JUMP",
        "9d3": "DM(I1, M0) = R0",
        "9d4": "R0 = LSHIFT R0 BY -2",
        "9d5": "R1 = 0x01400000",
        "9d6": "R0 = R0 + R1",
        "9d7": "I6 = DM(0x00030101)",
        "9d8": "I7 = R0",
        "9d9": "R0 = 0x05800B0B",
        "9da": "DM(I7, M1) = R0",
        "9db": "R0 = DM(I6, M1)",
        "9f3": "IF FLAG1_IN, JUMP",
        "9f4": "RTS (DB)",
        "9f5": "R0 = I7",
        "9f6": "DM(I1, M0) = R0",
        "9f7": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x3b slot {slot} missing {fragment}")

    stores = sum("DM(I7, M1) = R0" in lines.get(f"{slot:03x}", "") for slot in range(0x9da, 0x9f7))
    reads = sum("R0 = DM(I6, M1)" in lines.get(f"{slot:03x}", "") for slot in range(0x9da, 0x9f7))
    if stores != 13 or reads != 12:
        raise SystemExit(f"SHARC opcode-0x3b expected 13 stores/12 reads, got {stores}/{reads}")

    print("PASS: SHARC opcode-0x3b fixed-source table-copy bridge contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
