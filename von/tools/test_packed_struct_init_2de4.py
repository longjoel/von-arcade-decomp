#!/usr/bin/env python3
"""Check the i960 packed-struct init bridge contract at 0x2de4-0x2df0."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"

LINE_RE = re.compile(r"^\s*([0-9a-f]+):\s*[0-9a-f ]*\t(.*)$")

# Fall-through struct init between the average loop tail and the packed
# head: stores constant 0x4f at struct+0x10 and saves the caller link g14
# into the struct. Reached only by falling through from 0x2de0.
BRIDGE = {
    0x2DE4: "lda\t0x4f,r5",
    0x2DE8: "stos\tr5,0x10(g1)",
    0x2DEC: "stos\tg14,(g1)",
}

# Shared boundary: the packed-state head owned by
# maincpu.io-packed-controller-state, which the bridge falls into.
PACKED_HEAD = {0x2DF0: "ld\t0x50249c,g0"}

# A branch into the bridge would end its fall-through-only nature and must
# update the ledger attestation together with this contract.
ENTRY_RES = [
    re.compile(r"\bb[a-z]*\t0x2de(4|8|c)\b"),
    re.compile(r"\bcall\t0x2de(4|8|c)\b"),
    re.compile(r",0x2de(4|8|c)\b"),
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
               for address, expected in {**BRIDGE, **PACKED_HEAD}.items()
               if program.get(address) != expected]
    if missing:
        raise SystemExit("struct-init bridge contract missing: " + "; ".join(missing))
    entered = sorted({line.strip() for line in text.splitlines()
                      if any(pattern.search(line) for pattern in ENTRY_RES)})
    if entered:
        raise SystemExit("struct-init bridge gained a branch entry: "
                         + "; ".join(entered[:8]))
    print("PASS: i960 packed-struct init bridge contract at 0x2de4-0x2df0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
