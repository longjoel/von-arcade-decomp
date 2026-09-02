#!/usr/bin/env python3
"""Validate opcode 0x42's recovered packed-coordinate/Euler operation."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_42.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode42.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        first_pass = ctypes.CDLL(str(library)).recovered_sharc_opcode_42_first_pass
        first_pass.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        first_pass.restype = None
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_42_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None
        packed = (ctypes.c_uint32 * 3)(0x3C00, 0x4000, 0x4200)
        matrix = (ctypes.c_float * 9)(
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
            0.0, 0.0, 1.0,
        )
        output = (ctypes.c_float * 3)()

        first_pass(packed, matrix, output)
        for actual, wanted in zip(output, (1.0, 2.0, 3.0)):
            assert math.isclose(actual, wanted, abs_tol=1e-6), (actual, wanted)

        matrix[:] = (0.0, -1.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)
        first_pass(packed, matrix, output)
        for actual, wanted in zip(output, (2.0, -1.0, 3.0)):
            assert math.isclose(actual, wanted, abs_tol=1e-6), (actual, wanted)

        packed[0] = 0x12343C00
        first_pass(packed, matrix, output)
        assert math.isclose(output[0], 2.0, abs_tol=1e-6)

        packed[:] = (0x3C00, 0x4000, 0x4200)
        angles = (ctypes.c_int16 * 3)(0x4000, 0x4000, 0x4000)
        matrix[:] = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        initialize(packed, angles, matrix, output)
        for actual, wanted in zip(output, (1.0, 2.0, 3.0)):
            assert math.isclose(actual, wanted, abs_tol=1e-6), (actual, wanted)
        expected = (0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0)
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)

        matrix[:] = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
        initialize(packed, angles, matrix, output)
        expected = (7.0, 8.0, 9.0, -4.0, -5.0, -6.0, 1.0, 2.0, 3.0)
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-3), (actual, wanted)

    print("PASS: SHARC opcode-0x42 packed-coordinate/Euler operation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
