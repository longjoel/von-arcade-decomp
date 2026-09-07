#!/usr/bin/env python3
"""Check the i960 controller upload table contract at 0x2830-0x2846."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"
IMAGE = ROOT / "von/build/disasm/vonj-maincpu.bin"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Raw little-endian storage words exactly as listed.
STORAGE_WORDS = {
    0x2830: ".word\t0xd1511111",
    0x2834: ".word\t0xd151f171",
    0x2838: ".word\t0xf171d151",
    0x283C: ".word\t0xd151f171",
    0x2840: ".word\t0xd151d151",
    0x2844: ".word\t0x0000d151",
}

# The 22 bytes the 0x2850 loop consumes (r4 runs 21 down to -1). Distinct
# from the 21-byte io_setup_first sequence, which diverges at byte 13.
CONSUMED = bytes((
    0x11, 0x11, 0x51, 0xD1, 0x71, 0xF1, 0x51, 0xD1,
    0x51, 0xD1, 0x71, 0xF1, 0x71, 0xF1, 0x51, 0xD1,
    0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1,
))

# The sole static consumer: 0x2850 loads the table base into r5, counts
# r4 from 21 against -1, and issues the 0x27d8 status wait per byte.
CONSUMER = {
    0x2850: "lda\t0x2830,r5",
    0x2858: "lda\t0x1c00000,r7",
    0x2860: "mov\t21,r4",
    0x2864: "subo\t1,0,r6",
    0x2868: "ldob\t(r5),g4",
    0x286C: "subo\t1,r4,r4",
    0x2870: "stob\tg4,(r7)",
    0x2874: "bal\t0x27d8",
    0x2878: "cmpi\tr4,r6",
    0x287C: "addo\tr5,1,r5",
    0x2880: "bne\t0x2868",
    0x2884: "ret",
}


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
               for address, expected in {**STORAGE_WORDS, **CONSUMER}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("upload table contract missing: " + "; ".join(missing))
    image = IMAGE.read_bytes()
    if image[0x2830:0x2830 + len(CONSUMED)] != CONSUMED:
        raise SystemExit("upload table image bytes mismatch at 0x2830")
    if image[0x2846:0x2850] != bytes(0x2850 - 0x2846):
        raise SystemExit("upload table trailing bytes at 0x2846-0x284f must stay zero")
    print("PASS: i960 controller upload table contract at 0x2830-0x2846")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
