#!/usr/bin/env python3
"""Validate the four-vector transform recovered for SHARC opcode 0x09."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_09.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode09.so"
        subprocess.run(["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)], check=True)
        transform = ctypes.CDLL(str(library)).recovered_sharc_opcode_09_transform
        transform.argtypes = [ctypes.POINTER(ctypes.c_float)] * 3
        transform.restype = None
        state_vector = ctypes.CDLL(str(library)).recovered_sharc_opcode_09_state_vector
        state_vector.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_uint,
                                 ctypes.POINTER(ctypes.c_float)]
        state_vector.restype = None
        # The identified main-CPU caller emits three quadwords: four X values,
        # then four Y values, then four Z values.  The SHARC groups this FIFO
        # stream in threes, yielding (x0,y0,z0)..(x3,y3,z3).
        vectors = (ctypes.c_float * 12)(1, 2, 3, 4, 10, 20, 30, 40, 100, 200, 300, 400)
        coordinates = (ctypes.c_float * 3)()
        for vector, expected in enumerate(((1, 10, 100), (2, 20, 200),
                                           (3, 30, 300), (4, 40, 400))):
            state_vector(vectors, vector, coordinates)
            assert tuple(coordinates) == expected
        state_with_tail = (ctypes.c_float * 12)(
            1, 0, 0, 0, 1, 0, 0, 0, 1, 10, 20, 30
        )
        expected_state_vectors = ((1, 1, 1), (0, 0, 10),
                                  (0, 0, 20), (0, 0, 30))
        for vector, expected in enumerate(expected_state_vectors):
            state_vector(state_with_tail, vector, coordinates)
            assert tuple(coordinates) == expected
        identity = (ctypes.c_float * 9)(1, 0, 0, 0, 1, 0, 0, 0, 1)
        output = (ctypes.c_float * 12)()
        transform(vectors, identity, output)
        assert tuple(output) == (1, 10, 100, 2, 20, 200, 3, 30, 300, 4, 40, 400)
        matrix = (ctypes.c_float * 9)(1, 2, 3, 4, 5, 6, 7, 8, 9)
        transform(vectors, matrix, output)
        expected = []
        for vector in range(4):
            x, y, z = vectors[vector], vectors[4 + vector], vectors[8 + vector]
            expected.extend((x + 4*y + 7*z, 2*x + 5*y + 8*z, 3*x + 6*y + 9*z))
        for actual, wanted in zip(output, expected):
            assert math.isclose(actual, wanted, rel_tol=0.0, abs_tol=1e-4)
    print("PASS: SHARC opcode-0x09 four-vector matrix transform")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
