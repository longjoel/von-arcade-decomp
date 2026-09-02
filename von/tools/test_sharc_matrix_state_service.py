#!/usr/bin/env python3
"""Audit the 12-word SHARC state-preparation service at opcode 0x09."""

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
        raise SystemExit(f"SHARC opcode-0x09 slot {slot} missing {fragment}")


def main() -> int:
    lines = load_listing()
    require(lines, "1c2", "R0 = 0x00030200")
    require(lines, "1c3", "DM(0x00030101) = R0")

    input_slots = ("1c5", "1c7", "1c9", "1d5", "1d7", "1d9", "1e4", "1e6", "1e8", "1f3", "1f5", "1f7")
    for slot, register in zip(input_slots, ("R1", "R2", "R3") * 4):
        require(lines, slot, f"{register} = DM(I0, M0)")

    require(lines, "1ca", "I7 = DM(0x00030101)")
    require(lines, "1cb", "R4 = DM(0x00000000, I7)")
    for slot in ("1cc", "1cd", "1ce", "1cf", "1d0", "1d1", "1d2", "1d3", "1da", "1db", "1dc", "1dd", "1de", "1df", "1e0", "1e1", "1e9", "1ea", "1eb", "1ec", "1ed", "1ee", "1ef", "1f0", "1f8", "1f9", "1fa", "1fb", "1fc", "1fd", "1fe", "1ff", "200", "201", "202"):
        if not lines.get(slot, "").strip():
            raise SystemExit(f"SHARC opcode-0x09 coefficient slot {slot} is missing")

    for slot, fragment in {
        "1cf": "F5 = F8 + F12", "1d2": "F6 = F8 + F12", "1d7": "F7 = F8 + F12",
        "1de": "F9 = F8 + F12", "1e1": "F10 = F8 + F12", "1e6": "F11 = F8 + F12",
        "1ed": "F13 = F8 + F12", "1f0": "F14 = F8 + F12", "1f5": "F15 = F8 + F12",
    }.items():
        require(lines, slot, fragment)

    output_slots = {
        "203": "DM(0x00, I7) = R5", "205": "DM(0x01, I7) = R6", "206": "DM(0x00000002, I7) = R7",
        "207": "DM(0x00000003, I7) = R9", "208": "DM(0x00000004, I7) = R10", "209": "DM(0x00000005, I7) = R11",
        "20a": "DM(0x00000006, I7) = R13", "20b": "DM(0x00000007, I7) = R14", "20c": "DM(0x00000008, I7) = R15",
        "20d": "DM(0x00000009, I7) = R0", "20f": "DM(0x0000000A, I7) = R1", "210": "DM(0x0000000B, I7) = R2",
    }
    for slot, fragment in output_slots.items():
        require(lines, slot, fragment)
    require(lines, "20e", "RTS (DB)")

    print("PASS: SHARC opcode-0x09 12-input, coefficient-accumulation, 12-word state service")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
