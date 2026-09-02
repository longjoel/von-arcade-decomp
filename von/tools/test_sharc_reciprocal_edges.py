#!/usr/bin/env python3
"""Guard the reciprocal-service exception probe and its evidence labels."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PROBE = ROOT / "von/tools/probe_sharc_reciprocal_edges.lua"


def main() -> int:
    source = PROBE.read_text(encoding="utf-8")
    required_labels = (
        "1/0", "0/1", "+inf/1", "1/+inf", "nan/1", "1/nan",
        "denormal/1", "residual-1/0", "residual-1/inf", "residual-nan/1",
    )
    for label in required_labels:
        if f'"{label}"' not in source:
            raise SystemExit(f"reciprocal edge probe missing {label}")
    if source.count("{ 0x03,") != 7 or source.count("{ 0x04,") != 3:
        raise SystemExit("reciprocal edge probe does not contain the ten-vector sweep")
    if "space:read_u32(0x00884000)" not in source:
        raise SystemExit("reciprocal edge probe does not poll the output FIFO directly")
    if "VON_SHARC_RECIPROCAL_EDGES_LOG" not in source:
        raise SystemExit("reciprocal edge probe lacks a reproducible log override")
    print("PASS: SHARC opcode-0x03/0x04 reciprocal exception probe contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
