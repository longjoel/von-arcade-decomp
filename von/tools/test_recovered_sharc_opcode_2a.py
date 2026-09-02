#!/usr/bin/env python3
"""Validate opcode 0x2a's complete nine-element matrix scaling."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_2a.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode2a.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        scale = ctypes.CDLL(str(library)).recovered_sharc_opcode_2a_scale
        scale.argtypes = [ctypes.POINTER(ctypes.c_float), ctypes.c_float]
        scale.restype = None
        matrix = (ctypes.c_float * 9)(1.0, -2.0, 3.0, 4.0, 5.0, -6.0,
                                     7.0, 8.0, 9.0)
        scale(matrix, 2.0)
        assert list(matrix) == [2.0, -4.0, 6.0, 8.0, 10.0, -12.0,
                                14.0, 16.0, 18.0]

    print("PASS: SHARC opcode-0x2a matrix scale")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
