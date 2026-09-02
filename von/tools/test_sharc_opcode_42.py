#!/usr/bin/env python3
"""Audit the six-input packed-coordinate matrix service at opcode 0x42."""

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

    for slot, register in zip(
        ("b09", "b0b", "b0d", "b0f", "b11", "b13"),
        ("R0", "R1", "R2", "R13", "R14", "R15"),
    ):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x42 slot {slot} missing FIFO wait")
        read_slot = f"{int(slot, 16) + 1:03x}"
        if f"{register} = DM(I0, M0)" not in lines.get(read_slot, ""):
            raise SystemExit(f"SHARC opcode-0x42 slot {read_slot} missing {register} FIFO read")

    checks = {
        "b15": "I7 = DM(0x00030101)",
        "b16": "I6 = 0x00030141",
        "b17": "R5 = LSHIFT R0 BY 16",
        "b21": "R5 = LSHIFT R1 BY 16",
        "b2a": "R5 = LSHIFT R2 BY 16",
        "b41": "CALL (0x00020DBE) (DB)",
        "b44": "CALL (0x00020DC4) (DB)",
        "b5a": "CALL (0x00020DBE) (DB)",
        "b5d": "CALL (0x00020DC4) (DB)",
        "b73": "CALL (0x00020DBE) (DB)",
        "b76": "CALL (0x00020DC4) (DB)",
        "b86": "RTS (DB)",
        "b89": "IF FLAG0_IN, JUMP (0x00000B89)",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x42 slot {slot} missing {fragment}")

    state_stores = sum(
        "DM(" in lines.get(f"{slot:03x}", "")
        for slot in range(0xB33, 0xB89)
    )
    if state_stores < 18:
        raise SystemExit(f"SHARC opcode-0x42 expected matrix/state stores, got {state_stores}")

    print("PASS: SHARC opcode-0x42 six-input packed-coordinate matrix contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
