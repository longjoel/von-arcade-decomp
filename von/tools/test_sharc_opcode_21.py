#!/usr/bin/env python3
"""Audit the six-word SHARC parameter upload at opcode 0x21."""

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

    for slot, register in zip(("416", "418", "41a", "41c", "41e", "420"), ("R0", "R1", "R2", "R3", "R4", "R5")):
        if f"{register} = DM(I0, M0)" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x21 slot {slot} missing {register} FIFO read")
    for slot in ("415", "417", "419", "41b", "41d", "41f"):
        if "IF FLAG0_IN, JUMP" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x21 slot {slot} missing FIFO wait")

    checks = {
        "421": "I6 = 0x00030136",
        "422": "DM(I6, M1) = R0",
        "423": "DM(I6, M1) = R1",
        "424": "DM(I6, M1) = R2",
        "425": "DM(I6, M1) = R3",
        "426": "RTS (DB)",
        "427": "DM(I6, M1) = R4",
        "428": "DM(I6, M1) = R5",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x21 slot {slot} missing {fragment}")

    # Opcode 0x22 is the first confirmed consumer: it reloads the two plane
    # coefficients and four comparison thresholds from this block.
    consumer_checks = {
        "450": "R5 = DM(0x01, I6)",
        "451": "R6 = DM(0x04, I6)",
        "455": "R6 = DM(0x05, I6)",
        "459": "R6 = DM(0x02, I6)",
        "45c": "R6 = DM(0x03, I6)",
    }
    for slot, fragment in consumer_checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"opcode-0x22 consumer slot {slot} missing {fragment}")

    print("PASS: SHARC opcode-0x21 six-word parameter upload contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
