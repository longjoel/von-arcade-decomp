#!/usr/bin/env python3
"""Validate opcode 0x3c's canonical exceptional-frame behavior."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode3c.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2",
             str(ROOT / "von/i960/recovered_sharc_opcode_3c.c"),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        lib = ctypes.CDLL(str(library))
        frame = lib.recovered_sharc_opcode_3c_frame
        frame.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float,
                          ctypes.POINTER(ctypes.c_uint32)]
        frame.restype = None
        state = (ctypes.c_uint32 * 12)()
        for values in ((0.0, 1.0, 0.0), (0.0, 0.0, 0.0),
                       (math.nan, 1.0, 0.0)):
            frame(*values, state)
            assert list(state[:9]) == [0xffffffff] * 9
            assert list(state[9:]) == [0, 0, 0]

    print("PASS: SHARC opcode-0x3c canonical exceptional frame")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
