#!/usr/bin/env python3
"""Audit the statically recovered SHARC opcode-0x1e service shape."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def load_listing() -> dict[str, str]:
    result: dict[str, str] = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            result[slot] = body
    return result


def main() -> int:
    lines = load_listing()
    if "R0 = DM(I0, M0)" not in lines.get("3dd", ""):
        raise SystemExit("opcode 0x1e handler does not consume its first FIFO word")
    if "R15 = DM(I0, M0)" not in lines.get("3df", ""):
        raise SystemExit("opcode 0x1e handler does not consume its second FIFO word")
    if "R0 = LSHIFT R0 BY 16" not in lines.get("3e0", ""):
        raise SystemExit("opcode 0x1e handler lost signed-16 conversion")
    if "CALL (0x00020DBE)" not in lines.get("3e3", ""):
        raise SystemExit("opcode 0x1e handler lost its helper call")
    if "R1 = 0x38C9116D" not in lines.get("3e4", ""):
        raise SystemExit("opcode 0x1e handler lost its scale")
    if "F0 = F0 * F15" not in lines.get("3e8", ""):
        raise SystemExit("opcode 0x1e handler lost its second-input multiply")
    if "DM(I1, M0) = R0" not in lines.get("3e9", ""):
        raise SystemExit("opcode 0x1e handler lost its FIFO output")

    print("PASS: SHARC opcode-0x1e two-input scaled-output contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
