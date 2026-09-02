#!/usr/bin/env python3
"""Audit the three-input SHARC vector-normalization/state update at opcode 0x23."""

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

    for slot, register in zip(("46c", "46e", "470"), ("R0", "R1", "R2")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x23 slot {slot} missing {register} FIFO read")
    for slot in ("46b", "46d", "46f"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x23 slot {slot} missing FIFO wait")

    checks = {
        "471": "I6 = 0x00030180",
        "477": "F4 = RSQRTS F0",
        "478": "F12 = F4 * F4",
        "484": "F5 = F5 * F4",
        "485": "DM(0x00, I6) = R5",
        "487": "F4 = RSQRTS F8",
        "494": "R3 = DM(0x00, I6)",
        "496": "I7 = DM(0x00030101)",
        "497": "F1 = -F1,  R4 = DM(0x03, I7)",
        "49b": "DM(0x03, I7) = R9",
        "49d": "DM(0x06, I7) = R9",
        "4a1": "DM(0x04, I7) = R9",
        "4a3": "DM(0x00000007, I7) = R9",
        "4a7": "DM(0x05, I7) = R9",
        "4a9": "DM(0x00000008, I7) = R9",
        "4ad": "DM(0x00, I7) = R9",
        "4af": "DM(0x00000006, I7) = R9",
        "4b3": "DM(0x01, I7) = R9",
        "4b5": "DM(0x00000007, I7) = R9",
        "4b9": "DM(0x02, I7) = R9",
        "4ba": "RTS (DB)",
        "4bc": "DM(0x00000008, I7) = R9",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x23 slot {slot} missing {fragment}")

    # The first pass squares and accumulates all three FIFO lanes; the second
    # pass refines the reciprocal square root and retains the normalized lanes.
    for slot, fragment in {
        "473": "F8 = F0 * F4",
        "474": "F12 = F2 * F4",
        "475": "F12 = F1 * F4",
        "476": "F8 = F8 + F12",
        "477": "F4 = RSQRTS F0",
        "485": "F0 = F0 * F4",
        "486": "F2 = F2 * F4",
        "497": "F1 = -F1",
    }.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x23 normalization slot {slot} missing {fragment}")

    if "IF FLAG0_IN, JUMP" not in lines.get("4bd", ""):
        raise SystemExit("SHARC opcode-0x23 boundary does not reach opcode 0x24")

    print("PASS: SHARC opcode-0x23 vector-normalization/state-update contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
