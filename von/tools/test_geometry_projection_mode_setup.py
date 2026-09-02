#!/usr/bin/env python3
"""Audit the static mode-record setup used by the 0x6f6f0 callback tail."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    lines: dict[str, str] = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        address, body = line.split(":", 1)
        address = address.strip()
        if len(address) == 5 and all(char in "0123456789abcdef" for char in address):
            lines[address] = body

    setup_checks = {
        "6f900": "lda\t0x6f964,g14",
        "6f910": "lda\t(g0)[g0*2],g0",
        "6f914": "shlo\t3,g0,g0",
        "6f918": "lda\t0x6eb60,g4",
        "6f920": "ld\t0x14(g0)[g4],g5",
        "6f928": "ldl\t(g0)[g4],g6",
        "6f92c": "setbit\t6,0,g1",
        "6f940": "st\tg6,0x51bb24",
        "6f948": "st\tg5,0x884000",
        "6f950": "st\tg7,0x51bb28",
        "6f958": "st\tg4,0x51bb20",
        "6f960": "bx\t(g2)",
    }
    for address, fragment in setup_checks.items():
        if fragment not in lines.get(address, ""):
            raise SystemExit(f"mode setup slot {address} missing {fragment}")

    # The first word of each 24-byte mode record is the callback target.
    record_addresses = [
        "6eb70", "6eb88", "6eba0", "6ebb8", "6ebd0", "6ebe8",
        "6ec00", "6ec18", "6ec30", "6ec48", "6ec60", "6ec78",
        "6ec90", "6eca8", "6ecc0", "6ecd8",
    ]
    expected_targets = [
        "0006eb40", "0006eb40", "0006e8f0", "0006e6f0",
        "0006e7f0", "0006eb40", "0006e940", "0006eb40",
        "0006eb40", "0006ea40", "0006eb40", "0006eb40",
        "0006eb40", "0006eb40", "0006eb40", "0006eb40",
    ]
    for mode, (address, target) in enumerate(zip(record_addresses, expected_targets)):
        if target not in lines.get(address, ""):
            raise SystemExit(f"mode {mode} callback target changed at {address}")

    print("PASS: projection mode setup and all 16 callback-record targets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
