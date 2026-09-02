#!/usr/bin/env python3
"""Validate the finite angular projection recovered for SHARC opcode 0x25."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_25.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode25.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True,
            capture_output=True,
            text=True,
        )
        projection = ctypes.CDLL(str(library)).recovered_sharc_opcode_25_projection
        projection.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float,
                               ctypes.POINTER(ctypes.c_uint32)]
        projection.restype = None

        def run(x: float, y: float, z: float) -> tuple[int, int]:
            output = (ctypes.c_uint32 * 2)()
            projection(x, y, z, output)
            return output[0], output[1]

        assert run(1.0, 0.0, 0.0) == (0x80000000, 0)
        assert run(0.0, 0.0, 1.0) == (0, 0)
        assert run(1.0, 2.0, 3.0) == (0x00000B05, 0xFFFFE80B)
        assert run(1.0, 0.0, 1.0) == (0x00001FFF, 0)
        assert run(-1.0, 0.0, 1.0) == (0xFFFFE000, 0)
        assert run(1.0, 0.0, -1.0) == (0x00001FFF, 0x00007FFF)
        assert run(-1.0, 0.0, -1.0) == (0xFFFFE000, 0x00007FFF)
        assert run(0.0, 1.0, 0.0) == (0, 0xFFFFC000)
        assert run(0.0, -1.0, 0.0) == (0, 0x00003FFF)
        assert run(0.0, 1.0, 1.0) == (0, 0xFFFFE000)
        assert run(0.0, -1.0, 1.0) == (0, 0x00001FFF)

    print("PASS: SHARC opcode-0x25 angular projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
