#!/usr/bin/env python3
"""Validate opcode 0x38 packed decode and row-vector projection."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_38.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode38.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        project = ctypes.CDLL(str(library)).recovered_sharc_opcode_38_project
        project.argtypes = [
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        project.restype = None
        packed = (ctypes.c_uint32 * 3)(0x3C00, 0x4000, 0x4200)
        matrix = (ctypes.c_float * 9)(0.0, -1.0, 0.0, 1.0, 0.0, 0.0,
                                      0.0, 0.0, 1.0)
        output = (ctypes.c_float * 3)()

        project(packed, matrix, output)
        for actual, wanted in zip(output, (2.0, -1.0, 3.0)):
            assert math.isclose(actual, wanted, abs_tol=1e-6), (actual, wanted)

        packed[0] = 0x12343C00
        project(packed, matrix, output)
        assert math.isclose(output[0], 2.0, abs_tol=1e-6)

    print("PASS: SHARC opcode-0x38 packed decode and projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
