#!/usr/bin/env python3
"""Audit the packed-vector table-copy service at opcode 0x39."""

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
        "98a": "IF FLAG0_IN, JUMP",
        "98b": "R0 = DM(I0, M0)",
        "98c": "R1 = 0x01400000",
        "98d": "R0 = LSHIFT R0 BY -2",
        "98e": "R0 = R0 + R1",
        "98f": "I6 = DM(0x00030101)",
        "990": "I7 = R0",
        "991": "R0 = 0x05800B0B",
        "992": "DM(I7, M1) = R0",
        "993": "R0 = DM(I6, M1)",
        "9a8": "DM(I7, M1) = R0",
        "9aa": "R0 = DM(I6, M1)",
        "9ab": "DM(I7, M1) = R0",
        "9a9": "RTS (DB)",
        "9ac": "IF FLAG0_IN, JUMP",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x39 slot {slot} missing {fragment}")

    stores = sum("DM(I7, M1) = R0" in lines.get(f"{slot:03x}", "") for slot in range(0x992, 0x9ac))
    reads = sum("R0 = DM(I6, M1)" in lines.get(f"{slot:03x}", "") for slot in range(0x992, 0x9ac))
    if stores != 13 or reads != 12:
        raise SystemExit(f"SHARC opcode-0x39 expected 13 stores/12 reads, got {stores}/{reads}")

    print("PASS: SHARC opcode-0x39 packed-vector table-copy contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
