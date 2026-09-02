#!/usr/bin/env python3
"""Validate opcode 0x3a seeded copy and final-word output."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_3a.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode3a.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        copy = ctypes.CDLL(str(library)).recovered_sharc_opcode_3a_copy
        copy.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32), ctypes.POINTER(ctypes.c_uint32),
        ]
        copy.restype = ctypes.c_uint32
        table = (ctypes.c_uint32 * 12)(*range(12))
        destination = (ctypes.c_uint32 * 13)()
        output = ctypes.c_uint32()

        address = copy(0x00000100, table, destination, ctypes.byref(output))
        assert address == 0x01400040
        assert list(destination) == [0x05800B0B, *range(12)]
        assert output.value == 11

    print("PASS: SHARC opcode-0x3a seeded copy and output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
