#!/usr/bin/env python3
"""Guard the reproducible non-normal probe for SHARC helper 0x20d68."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_opcode_0f_nonfinite.lua"


def main() -> int:
    source = PROBE.read_text(encoding="utf-8")
    required = (
        "0x00000008",
        "0x0000000f",
        "0x7fc00000",
        "0xffc00000",
        "0x7f800000",
        "0xff800000",
        "0x00000001",
        "nonfinite-index=",
        "manager.machine:exit()",
    )
    for fragment in required:
        if fragment not in source:
            raise SystemExit(f"non-normal opcode-0x0f probe missing {fragment}")
    if source.count("{ ") != 8:
        raise SystemExit("non-normal opcode-0x0f probe does not contain eight vectors")
    print("PASS: SHARC opcode-0x0f non-normal probe contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
