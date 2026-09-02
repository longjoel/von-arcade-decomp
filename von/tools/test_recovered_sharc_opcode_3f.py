#!/usr/bin/env python3
"""Validate opcode 0x3f's normal mixed integer/float quotient."""

from __future__ import annotations

import ctypes
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_3f.c"


def bits(value: float) -> int:
    return struct.unpack("=I", struct.pack("=f", value))[0]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode3f.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        followup = ctypes.CDLL(str(library)).recovered_sharc_opcode_3f_followup
        followup.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        followup.restype = ctypes.c_uint32

        inputs = (ctypes.c_uint32 * 4)(0x3F800000, 0x40000000,
                                       bits(3.0), bits(4.0))
        assert followup(inputs) == bits(6.9765625)

        inputs[:] = (0x40000000, 0x40800000, bits(3.0), bits(5.0))
        assert followup(inputs) == bits(7.976744)

        inputs[:] = (0xFFFFFFF6, 2, bits(3.0), bits(4.0))
        assert followup(inputs) == bits(-11.0)
        inputs[:] = (0, 0, bits(3.0), bits(4.0))
        assert followup(inputs) == 0xffffffff
        inputs[:] = (1, 0, bits(3.0), bits(4.0))
        assert followup(inputs) == 0xffffffff
        inputs[:] = (0xffffffff, 1, bits(3.0), bits(4.0))
        assert followup(inputs) == bits(1.0)
        inputs[:] = (1, 1, bits(float("nan")), bits(4.0))
        assert followup(inputs) == 0xffffffff
        inputs[:] = (1, 1, bits(float("inf")), bits(4.0))
        assert followup(inputs) == 0x7f7fffff

    print("PASS: SHARC opcode-0x3f normal quotient model")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
