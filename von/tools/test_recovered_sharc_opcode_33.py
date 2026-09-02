#!/usr/bin/env python3
"""Validate the recovered SHARC opcode-0x33 transform contract."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_33.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode33.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_33_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_int16),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None

        translation = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        angles = (ctypes.c_int16 * 2)(0x4000, 0x4000)
        matrix = (ctypes.c_float * 9)(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        tail = (ctypes.c_float * 3)()
        initialize(translation, angles, matrix, tail)

        # Rx(pi/2) * Ry(pi/2), allowing the signed-angle helper residual.
        expected = (0.0, 0.0, 1.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)
        assert tuple(tail) == (1.0, 2.0, 3.0)

        matrix[:] = (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)
        initialize(translation, (ctypes.c_int16 * 2)(0, 0), matrix, tail)
        assert tuple(matrix) == (1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0)

    print("PASS: SHARC opcode-0x33 angle/translation model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
