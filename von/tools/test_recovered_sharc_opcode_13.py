#!/usr/bin/env python3
"""Test the recovered row-scaled matrix writeback for SHARC opcode 0x13."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_13.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-13-") as directory:
        library = Path(directory) / "libopcode_13.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        scale_rows = lib.recovered_sharc_opcode_13_scale_rows
        word_array = ctypes.c_uint32 * 9
        scale_rows.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_uint32),
                               ctypes.POINTER(ctypes.c_uint32)]
        scale_rows.restype = None
        vector = (ctypes.c_uint32 * 3)(0x40000000, 0x40400000, 0x40800000)
        matrix = word_array(
            0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0, 0x3f800000)
        output = word_array()
        scale_rows(vector, matrix, output)
        expected = (0x40000000, 0, 0, 0, 0x40400000, 0,
                    0, 0, 0x40800000)
        if tuple(output) != expected:
            raise SystemExit(f"opcode 0x13 mismatch: {tuple(output)!r}")
    print("recovered SHARC opcode-0x13 row-scaling vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
