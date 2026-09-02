#!/usr/bin/env python3
"""Guard the repeated related-record scale motif in geometry handlers."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
LISTING = ROOT / "von/build/disasm/vonj-maincpu.lst"


def window(lines: list[str], address: str, count: int = 18) -> list[str]:
    for index, line in enumerate(lines):
        if line.lstrip().startswith(address + ":"):
            return lines[index:index + count]
    raise SystemExit(f"missing handler address {address}")


lines = LISTING.read_text(encoding="utf-8").splitlines()
for address in ("df2e0", "df6c0", "df968", "dfc10", "e00f4", "e0150", "e05b0", "e060c", "e0cdc", "e1218", "e1274"):
    body = "\n".join(window(lines, address))
    if "ld\t0x58(r6)" not in body:
        raise SystemExit(f"{address}: missing related-record +0x58 load")

# The residual family uses the two-field product directly before its packet;
# the later rendering families use the same product before their output terms.
for address in ("df2e0", "df6c0", "df968", "dfc10", "e05b0", "e060c", "e0cdc", "e1218"):
    body = "\n".join(window(lines, address, 24))
    if "ld\t0x5c(r6)" not in body or "mulr" not in body:
        raise SystemExit(f"{address}: missing +0x58/+0x5c multiply sequence")

print("recovered geometry descriptor scale motif: ok")
