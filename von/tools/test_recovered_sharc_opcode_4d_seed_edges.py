#!/usr/bin/env python3
"""Guard the opcode-0x4d zero/NaN-seed probe and its entry shape."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_opcode_4d_edge.lua"
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def main() -> int:
    probe = PROBE.read_text(encoding="utf-8")
    for fragment in (
        'name = "zero-seed", vector = {0, 0x40800000, 0, 0}',
        'name = "nan-seed", vector = {0x7fc00001, 0x40800000, 0, 0x3f800000}',
        'header(0x4d)',
    ):
        if fragment not in probe:
            raise SystemExit(f"edge probe missing {fragment}")

    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body
    if "F4 = RSQRTS F1" not in lines.get("d08", ""):
        raise SystemExit("opcode-0x4d edge path lost its initial RSQRTS")
    if "IF LT" in lines.get("d08", "") or "IF LT" in lines.get("d09", ""):
        raise SystemExit("opcode-0x4d gained an unproven seed-sign branch")

    print("PASS: SHARC opcode-0x4d seed-edge probe contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
