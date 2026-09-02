#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x1a affine state-output model."""

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_1a.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-1a-") as directory:
        library = Path(directory) / "libopcode_1a.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        affine = lib.recovered_sharc_opcode_1a_affine
        words3 = ctypes.c_uint32 * 3
        words12 = ctypes.c_uint32 * 12
        affine.argtypes = [ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        affine.restype = None

        vector = words3(0x3f800000, 0x40000000, 0x40400000)
        state = words12(
            0x3f800000, 0, 0,
            0, 0x3f800000, 0,
            0, 0, 0x3f800000,
            0x41200000, 0x41a00000, 0x41f00000,
        )
        output = words3()
        affine(vector, state, output)
        expected = (0x41300000, 0x41b00000, 0x42040000)
        if tuple(output) != expected:
            raise SystemExit(f"opcode 0x1a mismatch: {tuple(output)!r}")

    print("recovered SHARC opcode-0x1a affine vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
