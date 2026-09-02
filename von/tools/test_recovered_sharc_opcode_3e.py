#!/usr/bin/env python3
"""Validate opcode 0x3e operand ordering and Euclidean distance."""

from __future__ import annotations

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_3e.c"


def bits(value: float) -> int:
    return struct.unpack("=I", struct.pack("=f", value))[0]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode3e.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        distance = ctypes.CDLL(str(library)).recovered_sharc_opcode_3e_distance
        distance.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        distance.restype = ctypes.c_uint32

        inputs = (ctypes.c_uint32 * 4)(bits(3.0), bits(0.0), bits(4.0), bits(0.0))
        result = distance(inputs)
        assert result == bits(5.0)

        inputs[:] = (bits(8.0), bits(5.0), bits(12.0), bits(8.0))
        assert distance(inputs) == bits(5.0)

        inputs[:] = (bits(0.0), bits(0.0), bits(0.0), bits(0.0))
        assert distance(inputs) == 0xffffffff
        inputs[:] = (bits(float("nan")), bits(0.0), bits(1.0), bits(0.0))
        assert distance(inputs) == 0xffffffff

    print("PASS: SHARC opcode-0x3e distance model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
