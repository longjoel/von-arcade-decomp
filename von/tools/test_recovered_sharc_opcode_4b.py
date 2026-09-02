#!/usr/bin/env python3
"""Validate the finite-path C predicate recovered for SHARC opcode 0x4b."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_4b.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode4b.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        predicate = ctypes.CDLL(str(library)).recovered_sharc_opcode_4b_predicate
        predicate.argtypes = [ctypes.c_float] * 4 + [ctypes.POINTER(ctypes.c_float)]
        predicate.restype = ctypes.c_uint32
        state = (ctypes.c_float * 9)(0.0, 0.0, 0.0, 4.0, 0.0, 2.0,
                                     1.0 / 3.0, 0.5, 3.0)

        assert predicate(0.0, 1.0, 0.0, 0.0, state) == 1
        assert predicate(0.0, -2.0, 0.0, 4.0, state) == 2
        assert predicate(1.0, -2.0, 0.0, 1.0, state) == 0
        assert predicate(1.0, -2.0, 0.0, 4.0, state) == 0
        zero_bound_state = (ctypes.c_float * 9)(0.0, 0.0, 0.0, 0.0, 0.0,
                                               2.0, 1.0 / 3.0, 0.5, 3.0)
        assert predicate(1.0, -2.0, 0.0, 0.0, zero_bound_state) == 2

        expected = 0.9428090416
        horizontal = math.hypot(1.0, 0.0)
        radius = math.hypot(horizontal, 2.0)
        bound = math.hypot(2.0 * horizontal / radius, (1.0 / 3.0) * -2.0 / radius)
        assert math.isclose(bound, expected, rel_tol=0.0, abs_tol=1e-6)

    print("PASS: SHARC opcode-0x4b finite-path C predicate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
