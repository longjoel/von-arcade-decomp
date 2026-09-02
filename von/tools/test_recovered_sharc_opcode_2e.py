#!/usr/bin/env python3
"""Validate the packed decoder and rotation contract for opcode 0x2e."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_2e.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode2e.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        initialize = ctypes.CDLL(str(library)).recovered_sharc_opcode_2e_initialize
        initialize.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
        ]
        initialize.restype = None
        packed = (ctypes.c_uint32 * 3)(0x3C00, 0x4000, 0)
        angles = (ctypes.c_uint32 * 3)(0, 0, 0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        initialize(packed, angles, matrix, tail)
        assert list(matrix) == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                0.0, 0.0, 1.0]
        assert math.isclose(tail[0], 1.0, abs_tol=1e-7)
        assert math.isclose(tail[1], 2.0, abs_tol=1e-7)
        assert math.isclose(tail[2], 2.0 ** -15, abs_tol=1e-7)

        angles[:] = (0x40, 0x40, 0x40)
        initialize(packed, angles, matrix, tail)
        expected = [0.0, 0.0, 1.0, 0.0, -1.0, 0.0, 1.0, 0.0, 0.0]
        for actual, wanted in zip(matrix, expected):
            assert math.isclose(actual, wanted, abs_tol=2e-4), (actual, wanted)

    print("PASS: SHARC opcode-0x2e packed decode and composed rotation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
