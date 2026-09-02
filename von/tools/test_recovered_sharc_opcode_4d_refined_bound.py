#!/usr/bin/env python3
"""Validate opcode 0x4d's recovered finite-seed bound formula."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_4d_refined_bound.c"
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"


def main() -> int:
    lines = {}
    for line in LISTING.read_text(encoding="utf-8").splitlines():
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(char in "0123456789abcdef" for char in slot):
            lines[slot] = body

    checks = {
        "d1b": "F1 = F0 * F5",
        "d1c": "F1 = F1 * F7",
        "d1d": "F0 = F0 * F6",
        "d1e": "F0 = F0 * F7",
        "d1f": "F8 = F1 * F4",
        "d20": "F12 = F0 * F4",
        "d21": "F0 = F8 + F12",
        "d2f": "F9 = F0 * F4",
    }
    for slot, fragment in checks.items():
        if fragment not in lines.get(slot, ""):
            raise SystemExit(f"SHARC opcode-0x4d bound slot {slot} missing {fragment}")

    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "bound.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        bound = ctypes.CDLL(str(library)).recovered_sharc_opcode_4d_refined_bound
        bound.argtypes = [ctypes.c_float] * 4
        bound.restype = ctypes.c_float

        cases = [
            # (dx, dy, dz, fourth input, expected coefficient * input)
            (1.0, 2.0, 0.0, 1.0, 0.9428090416),
            (1.0, 4.0, 0.0, 1.0, 0.5829830625),
            (3.0, 4.0, 0.0, 1.0, 1.2292726049),
            (3.0, 4.0, 0.0, 4.0, 4.9170904196),
        ]
        for dx, dy, dz, fourth, expected in cases:
            actual = float(bound(dx, dy, dz, fourth))
            if not math.isclose(actual, expected, rel_tol=0, abs_tol=2e-6):
                raise SystemExit(f"bound mismatch: got {actual}, expected {expected}")

        assert math.isnan(float(bound(0.0, 4.0, 0.0, 0.0)))
        assert math.isnan(float(bound(math.nan, 4.0, 0.0, 1.0)))

    print("PASS: SHARC opcode-0x4d refined bound formula")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
