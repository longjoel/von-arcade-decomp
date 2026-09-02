#!/usr/bin/env python3
"""Validate opcode 0x37 identity reset and direct tail placement."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_37.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode37.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        reset = ctypes.CDLL(str(library)).recovered_sharc_opcode_37_reset
        reset.argtypes = [
            ctypes.POINTER(ctypes.c_float), ctypes.POINTER(ctypes.c_float),
            ctypes.POINTER(ctypes.c_float),
        ]
        reset.restype = None
        translation = (ctypes.c_float * 3)(1.0, 2.0, 3.0)
        matrix = (ctypes.c_float * 9)()
        tail = (ctypes.c_float * 3)()

        reset(translation, matrix, tail)
        assert list(matrix) == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0,
                                0.0, 0.0, 1.0]
        assert list(tail) == [1.0, 2.0, 3.0]

    print("PASS: SHARC opcode-0x37 identity reset and tail")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
