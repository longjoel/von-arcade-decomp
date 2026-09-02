#!/usr/bin/env python3
"""Validate the recovered SHARC opcode-0x34 staged transform contract."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_34.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode34.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_34_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None

        first = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        second = (ctypes.c_float * 3)(4.0, 5.0, 6.0)
        angles = (ctypes.c_int16 * 2)(0, 0)
        matrix = (ctypes.c_float * 9)(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        tail = (ctypes.c_float * 3)(10.0, 20.0, 30.0)
        initialize(first, angles, second, matrix, tail)
        assert tuple(tail) == (15.0, 27.0, 39.0)

        first[:] = (0.0, 0.0, 0.0)
        second[:] = (0.0, 0.0, 0.0)
        angles[:] = (0x4000, 0x4000)
        matrix[:] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        tail[:] = (0.0, 0.0, 0.0)
        initialize(first, angles, second, matrix, tail)
        expected = (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)
        assert tuple(tail) == (0.0, 0.0, 0.0)

    print("PASS: SHARC opcode-0x34 staged transform model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
