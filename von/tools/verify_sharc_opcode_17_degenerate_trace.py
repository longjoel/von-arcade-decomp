#!/usr/bin/env python3
"""Verify a zero-y-plane record taking the normal exact-zero helper path."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", type=Path)
    parser.add_argument("probe_log", type=Path)
    args = parser.parse_args()

    probe = args.probe_log.read_text(encoding="utf-8")
    if probe.count("record=2") != 4:
        raise SystemExit("degenerate probe did not run all four record-2 cases")

    trace = args.trace.read_text(encoding="utf-8", errors="replace")
    if trace.count("vonj_sharc_20de1_step: pc=020de1 ") != 1:
        raise SystemExit("record-2 probe did not isolate one helper invocation")
    if "vonj_sharc_20de1_step: pc=020e4d " not in trace:
        raise SystemExit("record-2 probe did not take the normal helper return")
    if "vonj_sharc_geometry: pc=20e4d r0=00000000" not in trace:
        raise SystemExit("record-2 normal return was not exact zero")
    if "vonj_sharc_output: pc=020387 address=00c00000 data=00000000" not in trace:
        raise SystemExit("record-2 probe lacks the emitted exact-zero helper result")
    if "vonj_sharc_20de1_step: pc=020e50 " in trace:
        raise SystemExit("record-2 zero-plane case incorrectly took the -0.1 sentinel")

    print("PASS: SHARC opcode-0x17 zero-plane record uses normal exact-zero path")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
