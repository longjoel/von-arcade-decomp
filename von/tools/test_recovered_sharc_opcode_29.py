#!/usr/bin/env python3
"""Validate the opcode-0x29 reset, translation, and Y-rotation contract."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_29.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode29.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_29_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int16,
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None
        translation = (ctypes.c_float * 3)(10.0, 20.0, 30.0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        initialize(translation, 0, matrix, tail)
        assert list(matrix) == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                0.0, 0.0, 1.0]
        assert list(tail) == [10.0, 20.0, 30.0]

        initialize(translation, 0x4000, matrix, tail)
        assert math.isclose(matrix[0], 0.0, abs_tol=2e-4)
        assert matrix[2] > 0.999
        assert matrix[6] < -0.999
        assert math.isclose(matrix[8], 0.0, abs_tol=2e-4)

        initialize(translation, -0x4000, matrix, tail)
        assert matrix[2] < -0.999
        assert matrix[6] > 0.999

    print("PASS: SHARC opcode-0x29 state initializer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
