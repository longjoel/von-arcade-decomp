#!/usr/bin/env python3
"""Verify the SHARC opcode-0x00-0x02 scalar ALU models.

Nine live-hardware goldens from von/build/probe_sharc_opcode_00_02.lua
and von/build/probe_sharc_chop.lua: exact cases plus four
one-ulp chop-vs-nearest discriminators that all favor truncation.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_scalar_alu_00_02.c"

CASES = [
    ("sharc_scalar_fadd", 0x3FC00000, 0x40100000, 0x40700000),
    ("sharc_scalar_fadd", 0x3DCCCCCD, 0x3E4CCCCD, 0x3E999999),
    ("sharc_scalar_fadd", 0x3F800000, 0x3DCCCCCD, 0x3F8CCCCC),
    ("sharc_scalar_fsub", 0x40B00000, 0x3FA00000, 0x40880000),
    ("sharc_scalar_fsub", 0x3F800000, 0x3F800000, 0x00000000),
    ("sharc_scalar_fsub", 0x3E99999A, 0x3DCCCCCD, 0x3E4CCCCD),
    ("sharc_scalar_fmul", 0x3FC00000, 0x40100000, 0x40580000),
    ("sharc_scalar_fmul", 0xBF800000, 0x40000000, 0xC0000000),
    ("sharc_scalar_fmul", 0x3DCCCCCD, 0x3DCCCCCD, 0x3C23D70A),
]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-alu-") as directory:
        library = Path(directory) / "scalar-alu.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        for name, a, b, expected in CASES:
            fn = getattr(lib, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
            got = fn(a, b)
            assert got == expected, f"{name} {a:#x} {b:#x}: {got:#x}"
        print("PASS: scalar ALU x9 incl. 4 chop discriminators")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
