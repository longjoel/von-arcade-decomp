#!/usr/bin/env python3
"""Audit the shared two-input floating-point reduction helper at 0x20d68."""

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
        "d68": "I7 = 0x00030300",
        "d69": "F1 = PASS F1",
        "d6a": "IF EQ, JUMP (0x00020DBB)",
        "d6c": "R4 = LOGB F0,  R7 = R0",
        "d6d": "R1 = LOGB F1,  R15 = R1",
        "d6b": "IF LT, R2 = DM(0x0B, I7)",
        "d6e": "R1 = R4 - R1",
        "d6f": "COMP(R1, R4)",
        "d70": "IF GE, JUMP (0x00020DB8)",
        "d73": "IF LE, JUMP (0x00020DB5)",
        "d71": "R4 = -R4",
        "d72": "COMP(R1, R4)",
        "d74": "F7 = RECIPS F15",
        "d7b": "F0 = F1 * F7",
        "d7c": "F2 = PASS F2",
        "d7d": "IF NE, F0 = -F0",
        "d7e": "F15 = ABS F0",
        "d80": "IF LE, JUMP (0x00020D89)",
        "d89": "COMP(F15, F4)",
        "d8a": "IF LT, JUMP (0x00020D97)",
        "d8b": "R10 = R10 + 1",
        "d9a": "F1 = F15 * F15",
        "d9b": "F7 = F1 * F4",
        "d9c": "F7 = F7 + F4",
        "d9d": "F7 = F7 * F1",
        "d9e": "F12 = F1 + F4",
        "d9f": "F12 = F12 * F1",
        "da0": "F12 = F12 + F4",
        "da1": "F7 = RECIPS F12",
        "da8": "F7 = F1 * F7",
        "da9": "F7 = F7 * F15",
        "daa": "F15 = F7 + F15",
        "dab": "R1 = R10 - 1",
        "dad": "IF GT, F15 = -F15",
        "db0": "F2 = PASS F2",
        "db1": "IF NE, F15 = F2 - F15",
        "db3": "IF LT, F15 = -F15",
        "db2": "RTS (DB), F0 = PASS F0",
        "db5": "JUMP (0x00020DB0) (DB)",
        "db8": "JUMP (0x00020DB2) (DB)",
        "dbb": "F0 = PASS F0",
        "dbc": "IF NE, JUMP (0x00020DB8)",
        "dbd": "RTS",
        "dbe": "I7 = 0x0003030C",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20d68 slot {slot} missing {fragment}")

    for slot in ("d75", "d77", "d79", "d82", "d84", "d86", "d90", "d92", "d94", "da2", "da4", "da6"):
        if "F15 = F7 * F15" not in lines.get(slot, "") and "F12 = F7 * F12" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC helper-0x20d68 slot {slot} missing reciprocal refinement")

    if "3e8930a3" not in LISTING.read_text(encoding="utf-8"):
        raise SystemExit("SHARC angle table lost the rational-path anchor")

    print("PASS: SHARC helper-0x20d68 branched floating-point reduction contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
