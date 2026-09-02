#!/usr/bin/env python3
"""Audit the signed-angle quadrant probe and its live-output oracle."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_trig_quadrants.lua"
VERIFIER = ROOT / "von/tools/verify_sharc_trig_quadrants.py"


def main() -> int:
    source = PROBE.read_text(encoding="utf-8")
    for value in (
        "0x00000000", "0x00002000", "0x00004000", "0x00006000",
        "0x00007fff", "0xffff8000", "0xffffa000", "0xffffc000",
    ):
        if value not in source:
            raise SystemExit(f"quadrant probe missing {value}")
    for opcode in ("send(0x1b", "send(0x1c"):
        if opcode not in source:
            raise SystemExit(f"quadrant probe missing {opcode}")
    if not VERIFIER.exists() or "EXPECTED" not in VERIFIER.read_text(encoding="utf-8"):
        raise SystemExit("quadrant probe verifier is missing its output oracle")
    print("PASS: SHARC signed-angle quadrant probe contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
