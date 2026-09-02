#!/usr/bin/env python3
"""Validate the reusable C contracts for SHARC opcodes 0x2b and 0x2d."""

from __future__ import annotations

import ctypes
import random
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode2b2d.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2",
             str(ROOT / "von/i960/recovered_sharc_opcode_2b.c"),
             str(ROOT / "von/i960/recovered_sharc_opcode_2d.c"),
             "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        lib = ctypes.CDLL(str(library))
        status = lib.recovered_sharc_opcode_2b_status
        status.argtypes = []
        status.restype = ctypes.c_uint32
        passthrough = lib.recovered_sharc_opcode_2d_passthrough
        passthrough.argtypes = [ctypes.c_uint32]
        passthrough.restype = ctypes.c_uint32

        assert status() == 1
        values = [0, 1, 0x80000000, 0xffffffff]
        generator = random.Random(0x2D)
        values.extend(generator.getrandbits(32) for _ in range(256))
        for value in values:
            assert passthrough(value) == value

    print("PASS: SHARC opcode-0x2b/0x2d C contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
