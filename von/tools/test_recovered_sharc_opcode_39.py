#!/usr/bin/env python3
"""Validate opcode 0x39 destination derivation and seeded table copy."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_39.c"


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode39.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", str(SOURCE), "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        copy = ctypes.CDLL(str(library)).recovered_sharc_opcode_39_copy
        copy.argtypes = [
            ctypes.c_uint32, ctypes.POINTER(ctypes.c_uint32),
            ctypes.POINTER(ctypes.c_uint32),
        ]
        copy.restype = ctypes.c_uint32
        table = (ctypes.c_uint32 * 12)(*range(12))
        destination = (ctypes.c_uint32 * 13)()

        address = copy(0x00000100, table, destination)
        assert address == 0x01400040
        assert list(destination) == [0x05800B0B, *range(12)]

    print("PASS: SHARC opcode-0x39 seeded table copy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
