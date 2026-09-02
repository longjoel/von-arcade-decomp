#!/usr/bin/env python3
"""Audit the SHARC state-window services at opcodes 0x05-0x07."""

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


def require(lines: dict[str, str], slot: str, fragment: str) -> None:
    if fragment not in lines.get(slot, ""):
        raise SystemExit(f"SHARC state service slot {slot} missing {fragment}")


def main() -> int:
    lines = load_listing()

    # Opcode 0x05 -> 0x2016d: advance one of eight state windows and copy 12 words.
    require(lines, "16d", "R0 = DM(0x00030100)")
    require(lines, "16e", "R1 = 0x00000007")
    require(lines, "170", "IF GE, RTS (DB)")
    require(lines, "171", "R0 = R0 + 1")
    require(lines, "172", "DM(0x00030100) = R0")
    require(lines, "173", "I7 = DM(0x00030101)")
    require(lines, "174", "M7 = 0x0000000B")
    for slot in ("175", "177", "179", "17b", "17d", "17f", "181", "183", "185", "187", "189", "18b"):
        require(lines, slot, "R0 = DM(I7, M1)")
    for slot in ("176", "178", "17a", "17c", "17e", "180", "182", "184", "186", "188", "18a", "18d"):
        require(lines, slot, "DM(M7, I7) = R0")
    require(lines, "18c", "RTS (DB)")
    require(lines, "18e", "DM(0x00030101) = I7")

    # Opcode 0x06 -> 0x2018f: reverse one state-window step, with no FIFO access.
    require(lines, "18f", "R0 = DM(0x00030100)")
    require(lines, "191", "IF EQ, RTS")
    require(lines, "192", "R0 = R0 - 1")
    require(lines, "193", "DM(0x00030100) = R0")
    require(lines, "194", "R0 = DM(0x00030101)")
    require(lines, "197", "R0 = R0 - R1")
    require(lines, "198", "DM(0x00030101) = R0")

    # Opcode 0x07 -> 0x20199: receive and store a 12-word state vector.
    for index, slot in enumerate(("19a", "19c", "19e", "1a0", "1a2", "1a4", "1a6", "1a8", "1aa", "1ac", "1ae", "1b0")):
        require(lines, slot, f"R{index} = DM(I0, M0)")
    for index, slot in enumerate(("1b2", "1b3", "1b4", "1b5", "1b6", "1b7", "1b8", "1b9", "1ba", "1bb", "1bd", "1be")):
        require(lines, slot, f"DM(I7, M1) = R{index}")
    require(lines, "1b1", "I7 = DM(0x00030101)")

    print("PASS: SHARC opcode-0x05/0x06 state-window stepping and opcode-0x07 12-word load")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
