#!/usr/bin/env python3
"""Regression for the checked-in opcode-0x17 paired trace analysis."""

from __future__ import annotations

from pathlib import Path

from analyze_sharc_opcode_17_trace import summarize


ROOT = Path(__file__).resolve().parents[2]
TRACE = ROOT / "von/build/disasm/von-sharc-opcode-17-helper-sweep-reset45-delayed.trace"


def main() -> int:
    rows = summarize(TRACE)
    paired = [row for row in rows if row["return_pc"] is not None]
    normal = [row for row in paired if row["return_pc"] == "020e4c"]
    exact_zero = [row for row in normal if row["return"] == 0.0]
    if len(rows) != 12 or len(paired) != 12:
        raise SystemExit("delayed-reset trace no longer has twelve paired helper entries")
    if len(normal) != 12 or len(exact_zero) != 2:
        raise SystemExit("delayed-reset trace no longer separates normal zero returns")
    expected = (-0.0270270258, 0.23648648, 0.5, 1.02702701)
    actual = tuple(round(float(row["return"]), 7) for row in normal[:4])
    if actual != tuple(round(value, 7) for value in expected):
        raise SystemExit(f"unexpected first helper results: {actual}")
    print("PASS: opcode-0x17 trace analyzer paired-return oracle")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
