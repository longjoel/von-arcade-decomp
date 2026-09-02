#!/usr/bin/env python3
"""Validate opcode 0x36 tail addition and uniform matrix scale."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_36.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode36.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        update = ctypes.CDLL(str(library)).recovered_sharc_opcode_36_update
        update.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.c_float, ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        update.restype = None
        prior = (ctypes.c_float * 3)(10.0, 20.0, 30.0)
        delta = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        update(prior, delta, 2.0, matrix, tail)
        assert list(tail) == [11.0, 22.0, 33.0]
        assert list(matrix) == [2.0, 0.0, 0.0, 0.0, 2.0, 0.0,
                                0.0, 0.0, 2.0]

    print("PASS: SHARC opcode-0x36 tail add and uniform scale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
