#!/usr/bin/env python3
"""Verify the SHARC command-table opcode-to-target mapping."""

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

    expected = {
        0x00: "0x00020133",
        0x08: "0x000201BF",
        0x0f: "0x0002027E",
        0x10: "0x0002028E",
        0x11: "0x0002029E",
        0x12: "0x000202C5",
        0x13: "0x000202DC",
        0x14: "0x000202F6",
        0x15: "0x00020312",
        0x16: "0x0002032E",
        0x17: "0x0002034A",
        0x18: "0x0002038E",
        0x19: "0x00020397",
        0x1a: "0x0002039B",
        0x1b: "0x000203B6",
        0x1c: "0x000203C2",
        0x1d: "0x000203CE",
        0x1e: "0x000203DC",
        0x1f: "0x000203EA",
    }
    for opcode, target in expected.items():
        slot = f"{opcode + 0x99:03x}"
        fragment = f"DM(I0, M0) = {target}"
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode 0x{opcode:02x} slot {slot} missing {target}")

    for opcode in range(0x20, 0x4e):
        slot = f"{opcode + 0x99:03x}"
        if "DM(I0, M0) = 0x" not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode 0x{opcode:02x} slot {slot} is not a handler pointer")

    if "I0 = 0x00030300" not in lines.get("0e7", ""):
        raise SystemExit("SHARC command table slot 0xe7 no longer marks the constant-table boundary")
    if "DM(I0, M0) = 0x" in lines.get("0e7", ""):
        raise SystemExit("SHARC command table unexpectedly maps opcode 0x4e")

    print("PASS: SHARC command-table opcode-to-target mapping")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
