#!/usr/bin/env python3
"""Audit the recovered reciprocal and division-style SHARC service bodies."""

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

    if "MODE1 = 0x00018000" not in lines.get("080", ""):
        raise SystemExit("SHARC bootstrap does not select MODE1=0x00018000")

    common = {
        "flag0": "IF FLAG0_IN, JUMP",
        "read0": "R0 = DM(I0, M0)",
        "flag1": "IF FLAG0_IN, JUMP",
        "read1": "R12 = DM(I0, M0)",
        "constant": "R11 = 0x40000000",
        "recips": "F0 = RECIPS F12,  R7 = R0",
        "output_wait": "IF FLAG1_IN, JUMP",
        "output": "DM(I1, M0) = R0",
        "return": "RTS",
    }
    reciprocal = {
        "14b": "flag0", "14c": "read0", "14d": "flag1", "14e": "read1",
        "14f": "constant", "150": "recips", "158": "output_wait",
        "159": "output", "15a": "return",
    }
    division = {
        "15b": "flag0", "15c": "read0", "15d": "flag1", "15e": "read1",
        "15f": "constant", "160": "recips", "16a": "output_wait",
        "16b": "output", "16c": "return",
    }
    for name, service in (("0x03", reciprocal), ("0x04", division)):
        for slot, key in service.items():
            if common[key] not in lines.get(slot, ""):
                raise SystemExit(f"SHARC opcode {name} slot {slot} missing {common[key]}")

    required_operations = {
        "0x03": {"151": "F12 = F0 * F12", "152": "F7 = F0 * F7,  F0 = F11 - F12", "157": "F0 = F0 * F7"},
        "0x04": {"161": "F12 = F0 * F12,  R2 = R12", "162": "F7 = F0 * F7,  F0 = F11 - F12,  R1 = R7", "168": "F0 = F0 * F2", "169": "F0 = F1 - F0"},
    }
    for name, operations in required_operations.items():
        for slot, fragment in operations.items():
            if fragment not in lines.get(slot, ""):
                raise SystemExit(f"SHARC opcode {name} slot {slot} missing {fragment}")

    print("PASS: SHARC MODE1 rounding contract plus opcode-0x03 reciprocal and opcode-0x04 division service contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
