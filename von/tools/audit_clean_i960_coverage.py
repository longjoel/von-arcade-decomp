#!/usr/bin/env python3
"""Reject a clean-image run that executes outside generated i960 code."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pcs", required=True, type=Path)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--expected-seconds", type=float)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    generated_end = int(manifest["generated_code_bytes"])
    coverage = args.pcs.read_text(encoding="ascii")
    pcs = {
        int(line, 16)
        for raw in coverage.splitlines()
        if (line := raw.strip()) and not line.startswith("#")
    }
    if not pcs:
        raise SystemExit("error: PC coverage is empty")
    if any(pc < 0 or pc % 4 for pc in pcs):
        raise SystemExit("error: invalid or unaligned i960 PC")
    if args.expected_seconds is not None:
        if not math.isfinite(args.expected_seconds) or args.expected_seconds <= 0:
            raise SystemExit("error: expected seconds must be finite and positive")
        completion = re.findall(r"^# completed_time=([0-9.]+)$", coverage, re.MULTILINE)
        if len(completion) != 1:
            raise SystemExit("error: missing or duplicate capture completion time")
        elapsed = float(completion[0])
        if not math.isfinite(elapsed) or elapsed < args.expected_seconds:
            raise SystemExit(f"error: capture ended at {elapsed}s before {args.expected_seconds}s")
    escaped = sorted(pc for pc in pcs if pc >= generated_end)
    zero = 0 in pcs
    print(
        f"Clean i960 PC audit: {len(pcs)} visited instructions; "
        f"generated range 0x00000000-0x{generated_end:08x}"
    )
    if escaped:
        sample = ", ".join(f"0x{pc:08x}" for pc in escaped[:16])
        raise SystemExit(
            f"error: {len(escaped)} PCs escaped generated code; first: {sample}"
        )
    if zero:
        raise SystemExit("error: PC zero was executed; clean image hit an i960 exception path")
    print("PASS: every visited PC belongs to generated code")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
