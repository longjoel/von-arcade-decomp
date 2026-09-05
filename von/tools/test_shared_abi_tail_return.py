#!/usr/bin/env python3
"""Check the i960 shared ABI tail-return trampoline contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def main() -> int:
    text = LISTING.read_text(encoding="utf-8")
    required = (
        "27d8:", "mov\tg14,g0", "27dc:", "mov\t0,g14",
        "27e0:", "bx\t(g0)", "27e4:", "ret",
    )
    missing = [fragment for fragment in required if fragment not in text]
    if missing:
        raise SystemExit("ABI tail contract missing: " + ", ".join(missing))
    callers = text.count("bal\t0x27d8")
    if callers < 3:
        raise SystemExit(f"expected repeated ABI tail callers, found {callers}")
    print("PASS: shared i960 ABI tail-return trampoline contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
