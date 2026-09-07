#!/usr/bin/env python3
"""Check the i960 final setup table contract at 0x2890-0x28a6."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"
IMAGE = ROOT / "von/build/disasm/vonj-maincpu.bin"
MODEL = ROOT / "von/i960/recovered_io.c"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Raw little-endian storage words exactly as listed.
STORAGE_WORDS = {
    0x2890: ".word\t0xd1511111",
    0x2894: ".word\t0xd151f171",
    0x2898: ".word\t0xd151d151",
    0x289C: ".word\t0xd151d151",
    0x28A0: ".word\t0xd151d151",
    0x28A4: ".word\t0x0000d151",
}

# The 22 bytes the 0x28b0 loop consumes (r4 runs 21 down to -1). The first
# 21 match the io_setup_final model array; byte 22 is ROM-only.
CONSUMED = bytes((
    0x11, 0x11, 0x51, 0xD1, 0x71, 0xF1, 0x51, 0xD1,
    0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1,
    0x51, 0xD1, 0x51, 0xD1, 0x51, 0xD1,
))

# The sole static consumer: same 22-iteration shape as the 0x2850 uploader.
CONSUMER = {
    0x28B0: "lda\t0x2890,r5",
    0x28B8: "lda\t0x1c00000,r7",
    0x28C0: "mov\t21,r4",
    0x28C4: "subo\t1,0,r6",
    0x28C8: "ldob\t(r5),g4",
    0x28CC: "subo\t1,r4,r4",
    0x28D0: "stob\tg4,(r7)",
    0x28D4: "bal\t0x27d8",
    0x28D8: "cmpi\tr4,r6",
    0x28DC: "addo\tr5,1,r5",
    0x28E0: "bne\t0x28c8",
    0x28E4: "ret",
}


def parse_listing(text: str) -> dict[int, str]:
    program: dict[int, str] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            program[int(match.group(1), 16)] = match.group(2).strip()
    return program


def model_final() -> bytes:
    block = re.search(r"io_setup_final\[21\] = \{(.*?)\};", MODEL.read_text(encoding="utf-8"), re.S)
    if not block:
        raise SystemExit("io_setup_final model array not found")
    return bytes(int(value, 16) for value in re.findall(r"0x([0-9a-f]{2})", block.group(1)))


def main() -> int:
    program = parse_listing(LISTING.read_text(encoding="utf-8"))
    missing = [f"{address:#x}: {expected}"
               for address, expected in {**STORAGE_WORDS, **CONSUMER}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("final setup table contract missing: " + "; ".join(missing))
    image = IMAGE.read_bytes()
    if image[0x2890:0x2890 + len(CONSUMED)] != CONSUMED:
        raise SystemExit("final setup table image bytes mismatch at 0x2890")
    if image[0x28A6:0x28B0] != bytes(0x28B0 - 0x28A6):
        raise SystemExit("final setup table trailing bytes at 0x28a6-0x28af must stay zero")
    if model_final() != CONSUMED[:21]:
        raise SystemExit("final setup table diverges from io_setup_final model")
    print("PASS: i960 final setup table contract at 0x2890-0x28a6")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
