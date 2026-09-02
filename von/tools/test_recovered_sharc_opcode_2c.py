#!/usr/bin/env python3
"""Validate the opcode-0x2c translation and composed rotation contract."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_2c.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode2c.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_2c_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None
        translation = (ctypes.c_float * 3)(10.0, 20.0, 30.0)
        angles = (ctypes.c_int16 * 3)(0, 0, 0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        initialize(translation, angles, matrix, tail)
        assert list(matrix) == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                0.0, 0.0, 1.0]
        assert list(tail) == [10.0, 20.0, 30.0]

        angles[:] = (0x4000, 0x4000, 0x4000)
        initialize(translation, angles, matrix, tail)
        expected = [0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0]
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)

        angles[:] = (0x1000, 0x2000, 0x3000)
        initialize(translation, angles, matrix, tail)
        mixed = [0.270568043, -0.653275669, 0.707123756,
                 0.957111716, 0.103503883, -0.270599425,
                 0.103585929, 0.750011921, 0.653262556]
        for actual, wanted in zip(matrix, mixed):
            assert math.isclose(actual, wanted, abs_tol=3e-4), (actual, wanted)

    print("PASS: SHARC opcode-0x2c translation and composed rotation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
