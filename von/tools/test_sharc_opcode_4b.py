#!/usr/bin/env python3
"""Audit the branched three-valued predicate at opcode 0x4b."""

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

    for slot, register in zip(("c76", "c79", "c7c", "c80"), ("R8", "R9", "R10", "R13")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4b slot {slot} missing {register} FIFO read")
    for slot in ("c75", "c78", "c7b", "c7f"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4b slot {slot} missing FIFO wait")

    checks = {
        "c74": "I6 = 0x00030157",
        "c77": "R12 = DM(0x00000000, I6)",
        "c7a": "R13 = DM(0x01, I6)",
        "c7d": "R14 = DM(0x02, I6)",
        "c7e": "IF GT, JUMP (0x00020CC4)",
        "c80": "F2 = F10 - F14",
        "c81": "R4 = R2",
        "c82": "F12 = F2 * F4",
        "c82": "F12 = F2 * F4",
        "c83": "F1 = F8 + F12",
        "c82": "R3 = DM(0x07, I6)",
        "c83": "R8 = DM(0x08, I6)",
        "c86": "R5 = DM(0x05, I6)",
        "c87": "R6 = DM(0x06, I6)",
        "c84": "F4 = RSQRTS F1",
        "c90": "CALL (0x00020D68)",
        "c91": "F4 = F4 * F12",
        "c92": "F1 = F1 * F4",
        "c93": "CALL (0x00020DBE)",
        "c94": "F1 = PASS F14",
        "c95": "F15 = F1 * F4",
        "c96": "CALL (0x00020DC4)",
        "c97": "F1 = F0 * F5",
        "c9e": "F4 = RSQRTS F0",
        "cac": "F4 = RSQRTS F15",
        "cba": "COMP(F0, F1)",
        "cbb": "IF LT, JUMP (0x00020CC0)",
        "cbc": "IF FLAG1_IN, JUMP",
        "cbd": "RTS (DB)",
        "cbe": "R0 = 0x00000002",
        "cbf": "DM(I1, M0) = R0",
        "cc0": "IF FLAG1_IN, JUMP",
        "cc1": "RTS (DB)",
        "cc2": "R0 = 0x00000000",
        "cc3": "DM(I1, M0) = R0",
        "cc4": "IF FLAG0_IN, JUMP",
        "cc5": "R0 = DM(I0, M0)",
        "cc6": "IF FLAG1_IN, JUMP",
        "cc7": "RTS (DB)",
        "cc8": "R0 = 0x00000001",
        "cc9": "DM(I1, M0) = R0",
        "cca": "I6 = 0x00030157",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4b slot {slot} missing {fragment}")
    if "F15 = F9 + F15" not in lines.get("c97", ""):
        raise SystemExit("SHARC opcode-0x4b slot c97 missing F15 = F9 + F15")

    print("PASS: SHARC opcode-0x4b branched three-valued predicate contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
