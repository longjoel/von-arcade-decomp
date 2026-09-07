#!/usr/bin/env python3
"""Check the i960 sampler-entry thunk contract at 0x2cd0-0x2cf8."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# The private thunk: loads 0x2ce4 into g14, launders through g0, returns.
PRIVATE_THUNK = {
    0x2CD0: "lda\t0x2ce4,g14",
    0x2CD8: "mov\tg14,g0",
    0x2CDC: "mov\t0,g14",
    0x2CE0: "bx\t(g0)",
    0x2CE4: "ret",
}

# The staged entry: loads 0x2d5c into g14 and falls through into the sampler
# body at 0x2cf8 (owned by maincpu.io-failure-input-sampler), whose first
# instruction moves the staged continuation into g2 for the bx (g2) at 0x2d58.
STAGED_ENTRY = {0x2CF0: "lda\t0x2d5c,g14"}
SHARED_BODY_HEAD = {0x2CF8: "mov\tg14,g2"}

# The attested direct entry: flag-dispatch calls the sampler head without
# staging g2 (its bal sits inside maincpu.flag-dispatch-2c70's 0x2cb0 arm).
DIRECT_ENTRY = {0x2CC4: "bal\t0x2cf8"}

# Any static branch/call to a thunk entry or continuation, any address-taken
# load of a thunk entry, or any table word holding these addresses would
# attest a caller the ledger does not record. (lda patterns cover entries
# only: the definitions' own continuation operands must not self-match.)
CALLER_RES = [
    re.compile(r"\bb[a-z]*\t0x2c(d0|f0|e4)\b"),
    re.compile(r"\bcall\t0x2c(d0|f0|e4)\b"),
    re.compile(r"\bld[a-z]*\t0x2c(d0|f0)\b"),
    re.compile(r",0x2c(d0|f0|e4)\b"),
    re.compile(r"\bb[a-z]*\t0x2d5c\b"),
    re.compile(r"\b0x00012c(d0|f0|e4)\b"),
    re.compile(r"\b0x00012d5c\b"),
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
               for address, expected in {**PRIVATE_THUNK, **STAGED_ENTRY,
                                         **SHARED_BODY_HEAD, **DIRECT_ENTRY}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("sampler-entry thunk contract missing: " + "; ".join(missing))
    attested = sorted({line.strip() for line in text.splitlines()
                       if any(pattern.search(line) for pattern in CALLER_RES)})
    if attested:
        # A newly discovered static referrer changes the unit's attestation,
        # so the ledger notes and this contract must be updated together.
        raise SystemExit("sampler-entry thunks gained a static referrer: "
                         + "; ".join(attested[:8]))
    print("PASS: i960 sampler-entry thunk contract at 0x2cd0-0x2cf8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
