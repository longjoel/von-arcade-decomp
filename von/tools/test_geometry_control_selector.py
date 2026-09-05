#!/usr/bin/env python3
"""Check the selector-zero geometry control pulse contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    text = LISTING.read_text(encoding="utf-8")
    required = (
        "6fec0:", "cmpibl\t1,g0,0x6ff1c", "6fec4:",
        "cmpibg\t0,g0,0x6ff1c", "6fee0:", "st\tg5,0x800030",
        "6fef4:", "stl\tr4,(g4)", "6fef8:", "st\tr6,0x804008",
        "6ff00:", "st\tr6,0x80400c", "6ff08:", "st\tr6,0x804000",
        "6ff10:", "st\tr6,0x804000", "6ff1c:", "ret",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise SystemExit("control pulse contract missing: " + ", ".join(missing))
    print("PASS: selector-zero geometry control pulse contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
