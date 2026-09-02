#!/usr/bin/env python3
"""Validate opcode 0x31's final projection transform and output."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_31.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode31.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        project = ctypes.CDLL(str(library)).recovered_sharc_opcode_31_project
        project.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.c_int16, ctypes.c_int16,
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        project.restype = None
        tail = (ctypes.c_float * 3)(10.0, 20.0, 30.0)
        vector = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        matrix = (ctypes.c_float * 9)()
        output = (ctypes.c_float * 3)()

        project(tail, 0, 0, vector, matrix, output)
        assert list(matrix) == [1.0, 0.0, -0.0, 0.0, 1.0, 0.0,
                                0.0, -0.0, 1.0]
        assert list(output) == [11.0, 22.0, 33.0]

        project(tail, 0x4000, 0x4000, vector, matrix, output)
        expected_matrix = [0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 0.0]
        for actual, wanted in zip(matrix, expected_matrix):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)
        for actual, wanted in zip(output, (12.0, 23.0, 31.0)):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)

    print("PASS: SHARC opcode-0x31 projection transform and output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
