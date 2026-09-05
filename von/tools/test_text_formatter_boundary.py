#!/usr/bin/env python3
"""Check the bounded general text formatter control-flow contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    text = LISTING.read_text(encoding="utf-8")
    required = (
        "f5100:", "call\t0xf5190", "f5190:", "ldob\t(r12),g0",
        "f5204:", "ld\t0xf5210[g4*4],g4", "f520c:", "bx\t(g4)",
        "f5210:", "f5bf4:", "call\t0x1cc40",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise SystemExit("formatter boundary missing: " + ", ".join(missing))
    print("PASS: general text formatter boundary contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
