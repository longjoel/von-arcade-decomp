#!/usr/bin/env python3
"""Verify the SHARC opcode-0x03/0x04 divide/residual models.

Live DRC goldens from von/build/probe_sharc_opcode_04{c,d,w,u}.lua:
the truncating Goldschmidt model matches all 13 divide and all 20
residual words bit-for-bit. The interpreter evaluates the same pass
in host round-to-nearest floats, so it diverges by design (e.g. 6/2
gives 0x40400000 there vs 0x403fffff here; (1.7,1/3) residual gives
0xb4000000 there vs 0x34000000 here); those words are emulator
artifacts, not hardware truth, and are recorded here only as
documentation.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_divide_03_04.c"

DIV_CASES = [
    (0x40C00000, 0x40000000, 0x403FFFFF),
    (0x40400000, 0x40000000, 0x3FBFFFFF),
    (0x40A00000, 0x40400000, 0x3FD55555),
    (0x3F000000, 0x3F000000, 0x3F7FFFFF),
    (0x42C80000, 0x41200000, 0x411FFFFF),
    (0x3EAAAAAB, 0x3EAAAAAB, 0x3F800000),
    (0x41100000, 0x3FC00000, 0x40BFFFFF),
    (0xC0400000, 0x40000000, 0xBFBFFFFF),
    (0x40C00000, 0xC0000000, 0xC03FFFFF),
    (0x40E00000, 0x40400000, 0x40155555),
    (0x42C80000, 0x40E00000, 0x41649249),
    (0x41100000, 0x40E00000, 0x3FA49249),
    (0x41200000, 0x40400000, 0x40555555),
]

RES_CASES = [
    (0x40C00000, 0x40000000, 0x35000000),
    (0x3FD9999A, 0x3EAAAAAB, 0x34000000),
    (0x3F800000, 0x40400000, 0x33800000),
    (0x40E00000, 0x40000000, 0x35000000),
    (0x3F800000, 0x41200000, 0x33800000),
    (0x40400000, 0x40000000, 0x34800000),
    (0x40A00000, 0x40400000, 0x35000000),
    (0x3F000000, 0x3F000000, 0x33000000),
    (0x42C80000, 0x41200000, 0x37800000),
    (0x41100000, 0x3FC00000, 0x35800000),
    (0xC0400000, 0x40000000, 0xB4800000),
    (0x40C00000, 0xC0000000, 0x35000000),
    (0x3DCCCCCD, 0x40400000, 0x32000000),
    (0x40A00000, 0x40E00000, 0x35000000),
    (0x40400000, 0x40E00000, 0x34800000),
]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-div-") as directory:
        library = Path(directory) / "divide.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", str(SOURCE), "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        for name, cases in (("sharc_divide_q", DIV_CASES),
                            ("sharc_divide_residual", RES_CASES)):
            fn = getattr(lib, name)
            fn.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
            fn.restype = ctypes.c_uint32
            for a, b, expected in cases:
                got = fn(a, b)
                assert got == expected, f"{name} {a:#x} {b:#x}: {got:#x}"
        print(f"PASS: SHARC 03/04 divide x{len(DIV_CASES)} "
              f"residual x{len(RES_CASES)} (DRC goldens)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
