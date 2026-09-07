#!/usr/bin/env python3
"""Check the i960 port-wait branch-thunk contract at 0x27f0-0x2828."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Dual-entry wait-branch: the top entry stages continuation 0x2824 and
# discards the caller link; the mid entry at 0x27f8 preserves the caller
# link through g0. Both spin on bit 0x20 of port 0x1c00002 clearing, then
# tail-branch through g0.
WAIT_BRANCH = {
    0x27F0: "lda\t0x2824,g14",
    0x27F8: "mov\tg14,g0",
    0x27FC: "mov\t0,g14",
    0x2800: "lda\t0x1c00002,g6",
    0x2808: "lda\t0xff,g5",
    0x280C: "ldob\t(g6),g4",
    0x2810: "addo\t31,1,g7",
    0x2814: "and\tg4,g7,g4",
    0x2818: "and\tg5,g4,g4",
    0x281C: "cmpibe\t0,g4,0x280c",
    0x2820: "bx\t(g0)",
    0x2824: "ret",
}

# Attested mid-body entries: the 0x2990 indexed upload (after its copy loop)
# and the 0x2ab0 command builder (as its tail call) both enter past the lda,
# so the wait returns to the bal site once the port bit clears.
KNOWN_BALS = {
    0x2968: "bal\t0x27f8",
    0x2B9C: "bal\t0x27f8",
}

# Any other static branch/call to the top entry or continuation, any
# address-taken load of the top entry, or any table word holding these
# addresses would attest a referrer the ledger does not record. (The lda
# pattern covers the top entry only: the definition's own continuation
# operand must not self-match.)
CALLER_RES = [
    re.compile(r"\bb[a-z]*\t0x27f0\b"),
    re.compile(r"\bcall\t0x27f0\b"),
    re.compile(r"\bld[a-z]*\t0x27f0\b"),
    re.compile(r",0x27f0\b"),
    re.compile(r"\bb[a-z]*\t0x2824\b"),
    re.compile(r"\bcall\t0x2824\b"),
    re.compile(r",0x2824\b"),
    re.compile(r"\b0x000127f0\b"),
    re.compile(r"\b0x00012824\b"),
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
               for address, expected in {**WAIT_BRANCH, **KNOWN_BALS}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("wait-branch thunk contract missing: " + "; ".join(missing))
    attested = sorted({line.strip() for line in text.splitlines()
                       if any(pattern.search(line) for pattern in CALLER_RES)})
    if attested:
        # A newly discovered static referrer changes the unit's attestation,
        # so the ledger notes and this contract must be updated together.
        raise SystemExit("wait-branch thunk gained a static referrer: "
                         + "; ".join(attested[:8]))
    print("PASS: i960 port-wait branch-thunk contract at 0x27f0-0x2828")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
