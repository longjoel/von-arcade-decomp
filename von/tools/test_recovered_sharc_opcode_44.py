#!/usr/bin/env python3
"""Validate the reusable C contract for SHARC opcode 0x44."""

from __future__ import annotations

import ctypes
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode44.so"
        subprocess.run(
            [
                "cc", "-shared", "-fPIC", "-O2",
                str(ROOT / "von/i960/recovered_sharc_opcode_44.c"),
                "-o", str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        lib = ctypes.CDLL(str(library))
        initialize = lib.recovered_sharc_opcode_44_initialize
        initialize.argtypes = [ctypes.POINTER(ctypes.c_uint32)]
        initialize.restype = None

        expected = (0x40000000, 0x3EAAAAAB, 0x3F000000, 0x40400000)
        for seed in (0, 1, 0xDEADBEEF, 0xFFFFFFFF):
            values = (ctypes.c_uint32 * 4)(*(seed ^ index for index in range(4)))
            initialize(values)
            assert tuple(values) == expected

    print("PASS: SHARC opcode-0x44 C constant initializer")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
