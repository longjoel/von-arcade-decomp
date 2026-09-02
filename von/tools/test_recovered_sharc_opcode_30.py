#!/usr/bin/env python3
"""Validate opcode 0x30's transformed tail and scaled-Z rebuild."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_30.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode30.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        update = ctypes.CDLL(str(library)).recovered_sharc_opcode_30_update
        update.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.c_int16, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        update.restype = None
        translation = (ctypes.c_float * 3)(2.0, 3.0, 4.0)
        prior = (ctypes.c_float * 9)(1.0, 2.0, 3.0, 4.0, 5.0, 6.0,
                                     7.0, 8.0, 9.0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        update(translation, prior, 1.0, 0, matrix, tail)
        assert list(tail) == [42.0, 51.0, 60.0]
        assert list(matrix) == [1.0, -0.0, 0.0, 0.0, 1.0, 0.0,
                                0.0, 0.0, 1.0]

        update(translation, prior, 0.5, 0x4000, matrix, tail)
        assert math.isclose(matrix[0], 0.0, abs_tol=2e-4)
        assert math.isclose(matrix[1], -0.5, abs_tol=2e-4)
        assert math.isclose(matrix[3], 0.5, abs_tol=2e-4)
        assert math.isclose(matrix[4], 0.0, abs_tol=2e-4)
        assert math.isclose(matrix[8], 0.5, abs_tol=2e-4)
        assert list(tail) == [42.0, 51.0, 60.0]

    print("PASS: SHARC opcode-0x30 transformed tail and scaled-Z rebuild")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
