#!/usr/bin/env python3
"""Test the recovered matrix-vector tail accumulator for SHARC opcode 0x12."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_12.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-12-") as directory:
        library = Path(directory) / "libopcode_12.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        accumulate = lib.recovered_sharc_opcode_12_accumulate
        accumulate.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_uint32)]
        accumulate.restype = None
        vector = (ctypes.c_uint32 * 3)(0x40000000, 0x40400000, 0x40800000)
        matrix = (ctypes.c_uint32 * 9)(
            0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000)
        tail = (ctypes.c_uint32 * 3)(0x3f800000, 0x40000000, 0x40400000)
        output = (ctypes.c_uint32 * 3)()
        accumulate(vector, matrix, tail, output)
        expected = (0x40400000, 0x40a00000, 0x40e00000)
        if tuple(output) != expected:
            raise SystemExit(f"opcode 0x12 mismatch: {tuple(output)!r}")
    print("recovered SHARC opcode-0x12 matrix-vector vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
