#!/usr/bin/env python3
"""Audit the eight-input, three-output SHARC vector service at opcode 0x0b."""

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

    input_slots = ("21c", "21e", "220", "222", "224", "226", "228", "22a", "22c")
    input_registers = ("R8", "R9", "R10", "R12", "R13", "R14", "R8", "R8", "R8")
    for slot, register in zip(input_slots, input_registers):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0b slot {slot} missing {register} FIFO read")

    for slot in ("21d", "21f", "221", "223", "225", "227", "229", "22b"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0b slot {slot} missing FIFO wait")

    checks = {
        "237": "F4 = RSQRTS F0",
        "238": "F12 = F4 * F4",
        "239": "F12 = F12 * F0",
        "243": "F4 = F4 * F12",
        "244": "F0 = F6 * F4",
        "245": "F1 = F9 * F4",
        "246": "F2 = F5 * F4",
        "247": "IF FLAG1_IN, JUMP",
        "248": "DM(I1, M0) = R0",
        "249": "IF FLAG1_IN, JUMP",
        "24a": "DM(I1, M0) = R1",
        "24b": "IF FLAG1_IN, JUMP",
        "24c": "DM(I1, M0) = R2",
        "24d": "RTS",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x0b slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x0b nine-input, RSQRT-refined, three-output vector contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
