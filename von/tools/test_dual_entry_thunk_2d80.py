#!/usr/bin/env python3
"""Check the i960 dual-entry thunk contract at 0x2d80-0x2d98."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Dual-entry link trampoline: the top entry discards the caller link and
# tails to the ret at 0x2d94; the mid entry at 0x2d88 preserves the caller
# link through g0 and returns to the caller.
TRAMPOLINE = {
    0x2D80: "lda\t0x2d94,g14",
    0x2D88: "mov\tg14,g0",
    0x2D8C: "mov\t0,g14",
    0x2D90: "bx\t(g0)",
    0x2D94: "ret",
}

# Attested mid-body entry: the flag-dispatch 0x2d60 arm bals past the lda,
# so the link returns to 0x2d70 (inside maincpu.flag-dispatch-2c70).
KNOWN_BAL = {0x2D6C: "bal\t0x2d88"}

# Any other static branch/call to the top entry or continuation, any
# address-taken load of the top entry, or any table word holding these
# addresses would attest a referrer the ledger does not record. (The lda
# pattern covers the top entry only: the definition's own continuation
# operand must not self-match.)
CALLER_RES = [
    re.compile(r"\bb[a-z]*\t0x2d8(0|94)\b"),
    re.compile(r"\bcall\t0x2d8(0|94)\b"),
    re.compile(r"\bld[a-z]*\t0x2d80\b"),
    re.compile(r",0x2d8(0|94)\b"),
    re.compile(r"\b0x00012d8(0|94)\b"),
]


def parse_listing(text: str) -> dict[int, str]:
    program: dict[int, str] = {}
    for line in text.splitlines():
        match = LINE_RE.match(line)
        if match:
            program[int(match.group(1), 16)] = match.group(2).strip()
    return program


def main() -> int:
    text = LISTING.read_text(encoding="utf-8")
    program = parse_listing(text)
    missing = [f"{address:#x}: {expected}"
               for address, expected in {**TRAMPOLINE, **KNOWN_BAL}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("dual-entry thunk contract missing: " + "; ".join(missing))
    attested = sorted({line.strip() for line in text.splitlines()
                       if any(pattern.search(line) for pattern in CALLER_RES)})
    if attested:
        # A newly discovered static referrer changes the unit's attestation,
        # so the ledger notes and this contract must be updated together.
        raise SystemExit("dual-entry thunk gained a static referrer: "
                         + "; ".join(attested[:8]))
    print("PASS: i960 dual-entry thunk contract at 0x2d80-0x2d98")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
