#!/usr/bin/env python3
"""Check the i960 continuation-thunk cluster contract at 0x2790-0x27d8."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Expected mnemonic text per address for the two private thunks.
PRIVATE_THUNKS = {
    0x2790: "lda\t0x27a4,g14",
    0x2798: "mov\tg14,g0",
    0x279C: "mov\t0,g14",
    0x27A0: "bx\t(g0)",
    0x27A4: "ret",
    0x27B0: "lda\t0x27c4,g14",
    0x27B8: "mov\tg14,g0",
    0x27BC: "mov\t0,g14",
    0x27C0: "bx\t(g0)",
    0x27C4: "ret",
}

# The third thunk only stages its continuation, then falls through into the
# shared 0x27d8 trampoline body owned by maincpu.shared-abi-tail-return-trampoline.
SHARED_THUNK_SETUP = {0x27D0: "lda\t0x27e4,g14"}
SHARED_THUNK_ENTRY = {0x27D8: "mov\tg14,g0"}

# Any static branch to a thunk entry/continuation, or any address-taken load
# of a thunk entry, would attest a caller for the unattested thunks.
CALLER_RES = [
    re.compile(r"\bb[a-z]*\t0x27(b0|d0|a4|c4|e4)\b"),
    re.compile(r"\bcall\t0x27(b0|d0|a4|c4|e4)\b"),
    re.compile(r"\bld[a-z]*\t0x27(b0|d0)\b"),
    re.compile(r",0x27(b0|d0|a4|c4|e4)\b"),
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
    missing = [
        f"{address:#x}: {expected}"
        for address, expected in {**PRIVATE_THUNKS, **SHARED_THUNK_SETUP, **SHARED_THUNK_ENTRY}.items()
        if program.get(address) != expected
    ]
    if missing:
        raise SystemExit("thunk cluster contract missing: " + "; ".join(missing))
    # The word 0x00012790 appears at table entry 0x132ec, but every sibling
    # entry addresses a 0x12xxxx data record, so a call-target role stays
    # SPECULATIVE (see the ledger unit's unresolved_behavior).
    if program.get(0x132EC) != ".word\t0x00012790":
        raise SystemExit("thunk cluster missing table word: 132ec should hold 0x00012790")
    attested = sorted({line.strip() for line in text.splitlines()
                       if any(pattern.search(line) for pattern in CALLER_RES)})
    if attested:
        # A newly discovered static caller changes the unit's attestation, so
        # the ledger notes and this contract must be updated together.
        raise SystemExit("thunk cluster gained a static caller: " + "; ".join(attested[:8]))
    print("PASS: i960 continuation-thunk cluster contract at 0x2790-0x27d8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
