#!/usr/bin/env python3
"""Validate opcode 0x3d transposed frame and singular boundaries."""

from __future__ import annotations

import ctypes
import math
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_3d.c"


def as_float(bits: int) -> float:
    return struct.unpack("=f", struct.pack("=I", bits))[0]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode3d.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        frame = ctypes.CDLL(str(library)).recovered_sharc_opcode_3d_frame
        frame.argtypes = [
            ctypes.c_float, ctypes.c_float, ctypes.c_float,
            ctypes.POINTER(ctypes.c_uint32),
        ]
        frame.restype = None
        state = (ctypes.c_uint32 * 12)()

        frame(3.0, 4.0, 12.0, state)
        horizontal = math.sqrt(153.0)
        expected = [12.0 / horizontal, 0.0, -3.0 / horizontal,
                    -12.0 / (13.0 * horizontal), horizontal / 13.0,
                    -48.0 / (13.0 * horizontal),
                    3.0 / 13.0, 4.0 / 13.0, 12.0 / 13.0]
        for actual_bits, wanted in zip(state[:9], expected):
            assert math.isclose(as_float(actual_bits), wanted, abs_tol=1e-6)
        assert list(state[9:]) == [0, 0, 0]

        frame(0.0, 1.0, 0.0, state)
        assert list(state[:9]) == [0xffffffff] * 9
        assert list(state[9:]) == [0, 0, 0]

        frame(math.nan, 1.0, 0.0, state)
        assert list(state[:9]) == [0xffffffff] * 9
        assert list(state[9:]) == [0, 0, 0]

    print("PASS: SHARC opcode-0x3d frame and singular boundaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
