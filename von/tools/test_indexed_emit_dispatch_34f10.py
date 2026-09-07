#!/usr/bin/env python3
"""Check the i960 indexed-emit dispatch contract at 0x34f10-0x34f8c."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Match-only dispatch head: derives a record index from 0x19a(r8), clamps
# it against 4 (default target 0x355d8), and indirect-branches through the
# five-entry table. Entered by fall-through from the shared prefix; the
# immediate predecessor selects the shared 0x358ac exit when bit 15 is set.
DISPATCH_HEAD = {
    0x34F10: "ld\t0x70(r8),g6",
    0x34F14: "ldos\t0x19a(r8),g4",
    0x34F18: "ld\t0x34(g6),g5",
    0x34F1C: "shlo\t16,g4,g4",
    0x34F20: "shri\t16,g4,g4",
    0x34F24: "cmpibge\tg4,g5,0x358ac",
    0x34F28: "ldos\t0x19a(r8),g4",
    0x34F2C: "ld\t0x30(g6),g5",
    0x34F30: "shlo\t16,g4,g4",
    0x34F34: "shri\t16,g4,g4",
    0x34F38: "lda\t(g4)[g4*2],g4",
    0x34F3C: "shlo\t2,g4,g4",
    0x34F40: "addo\tg5,g4,g4",
    0x34F44: "ldl\t(g4),g6",
    0x34F48: "stl\tg6,0x40(fp)",
    0x34F4C: "ld\t0x8(g4),g4",
    0x34F50: "st\tg4,0x48(fp)",
    0x34F54: "ldos\t0x30(r8),g4",
    0x34F58: "cmpibe\t0,g4,0x34f60",
    0x34F5C: "stos\tg0,0x19a(r8)",
    0x34F60: "ld\t0x40(fp),g4",
    0x34F64: "addo\tg4,2,g4",
    0x34F68: "cmpobl\t4,g4,0x355d8",
    0x34F6C: "ld\t0x34f78[g4*4],g4",
    0x34F74: "bx\t(g4)",
}

# Five table targets, all visited in the manual-01 match replay.
JUMP_TABLE = {
    0x34F78: ".word\t0x00035510",
    0x34F7C: ".word\t0x000355d8",
    0x34F80: ".word\t0x00034f8c",
    0x34F84: ".word\t0x0003503c",
    0x34F88: ".word\t0x0003528c",
}

# Entry context: shared-prefix instruction owned by no unit; the head is
# reached by falling through it when bit 15 is clear.
ENTRY_CONTEXT = {0x34F0C: "bbs\t15,g4,0x358ac"}


def parse_listing(text: str) -> dict[int, str]:
    program: dict[int, str] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            program[int(match.group(1), 16)] = match.group(2).strip()
    return program


def main() -> int:
    program = parse_listing(LISTING.read_text(encoding="utf-8"))
    missing = [f"{address:#x}: {expected}"
               for address, expected in {**DISPATCH_HEAD, **JUMP_TABLE,
                                         **ENTRY_CONTEXT}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("emit dispatch contract missing: " + "; ".join(missing))
    print("PASS: i960 indexed-emit dispatch contract at 0x34f10-0x34f8c")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
