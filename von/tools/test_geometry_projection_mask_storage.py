#!/usr/bin/env python3
"""Audit the dynamic storage boundary for projection mask tables."""

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

    checks = {
        "9baa4": "stq\tg8,0x50(fp)",
        "9baac": "ld\t0x5770f0,g4",
        "9bab4": "lda\t(g4)[g4*4],g4",
        "9babc": "ld\t0x9b8d0(g6),r7",
        "9bac8": "ld\t0x74(g0),r5",
        "9badc": "ld\t0x10(g0),g4",
        "9baf4": "ld\t0x8(g0),g5",
        "9bae8": "lda\t0x407e0000,r13",
        "9baf0": "addrl\tfp0,r12,g12",
        "9bb00": "addrl\tfp1,r12,g12",
        "9bb04": "cvtzri\tfp0,g4",
        "9bb0c": "cvtzri\tfp1,g5",
        "9bb10": "addo\t31,9,r4",
        "9bb30": "ld\t0x4(g6)[r15],r6",
        "9bb48": "ld\t(r6)[g1*4],g6",
        "9bc48": "ld\t0x562c80,g6",
        "9bc50": "shlo\tg4,3,g4",
        "9bc68": "and\tg4,g6,g4",
        "9bc6c": "shlo\tg2,g4,g4",
        "9bc70": "shro\t16,g4,g4",
        "9bc74": "subo\tg4,g5,g5",
        "9bc78": "lda\t0x4800(g5),g5",
        "9bc80": "and\tg7,g5,g5",
        "9bc84": "cmpoble\tg5,g13,0x9bc9c",
        "9bb8c": "st\tg6,0x562c80",
        "9bba4": "ld\t(r6)[g1*4],g5",
        "9bbb8": "st\tg5,0x562c84",
        "9bd68": "b\t0x9bd7c",
        "9bd6c": "st\tg14,0x562c84",
        "9bd74": "st\tg14,0x562c80",
    }
    for address, fragment in checks.items():
        if fragment not in lines.get(address, ""):
            raise SystemExit(f"projection mask storage slot {address} missing {fragment}")

    print("PASS: projection mask tables are dynamically derived and stored")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
