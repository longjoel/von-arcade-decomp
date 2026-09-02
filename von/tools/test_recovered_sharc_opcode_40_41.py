#!/usr/bin/env python3
"""Validate the reusable C contracts for SHARC opcodes 0x40 and 0x41."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCES = [
    ROOT / "von/i960/recovered_sharc_opcode_40.c",
    ROOT / "von/i960/recovered_sharc_opcode_41.c",
]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode40_41.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2", *(str(source) for source in SOURCES),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        lib = ctypes.CDLL(str(library))
        base = lib.recovered_sharc_opcode_40_base
        base.argtypes = [ctypes.c_uint32]
        base.restype = ctypes.c_uint32
        address = lib.recovered_sharc_opcode_41_address
        address.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        address.restype = ctypes.c_uint32
        extract = lib.recovered_sharc_opcode_41_extract
        extract.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
        extract.restype = ctypes.c_uint8

        for operand in range(0x10000):
            assert base(operand) == ((operand << 16) + 0x01C00000) & 0xFFFFFFFF
            derived = base(operand)
            word = (operand * 0x01010101) & 0xFFFFFFFF
            assert address(operand, derived) == (derived + (operand >> 2)) & 0xFFFFFFFF
            assert extract(operand, word) == ((word >> ((operand & 3) * 8)) & 0xFF)

    print("PASS: SHARC opcode-0x40/0x41 C contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
