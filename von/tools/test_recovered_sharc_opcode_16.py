#!/usr/bin/env python3
"""Test the recovered SHARC opcode-0x16 Z-axis rotation model."""

import ctypes
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_16.c"


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-16-") as directory:
        library = Path(directory) / "libopcode_16.so"
        subprocess.run(["cc", "-std=c99", "-O2", "-fPIC", "-shared",
                        str(SOURCE), "-o", str(library)], check=True)
        lib = ctypes.CDLL(str(library))
        rotate = lib.recovered_sharc_opcode_16_rotate_z
        words = ctypes.c_uint32 * 9
        rotate.argtypes = [ctypes.c_uint32, ctypes.c_uint32,
                           ctypes.POINTER(ctypes.c_uint32),
                           ctypes.POINTER(ctypes.c_uint32)]
        matrix = words(0x3f800000, 0, 0, 0, 0x3f800000, 0, 0, 0,
                       0x3f800000)
        output = words()
        rotate(0x3f800000, 0xb8492eef, matrix, output)
        expected = (0xb8492eef, 0xbf800000, 0x80000000, 0x3f800000,
                    0xb8492eef, 0, 0, 0, 0x3f800000)
        if tuple(output) != expected:
            raise SystemExit(f"opcode 0x16 mismatch: {tuple(output)!r}")
    print("recovered SHARC opcode-0x16 Z-rotation vectors: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
