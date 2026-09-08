#!/usr/bin/env python3
"""Verify the SHARC opcode-0x07 verbatim affine-state store.

Pins the 12-word identity copy, then replays four live-hardware
trials end to end: store the trial state, transform the trial vector
with the trusted opcode-0x1a model, and compare against the response
words captured by von/build/probe_sharc_opcode_07_store.lua. Any
transpose, negation, scaling, or quantization in 0x07 would break
the chain.
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_opcode_07_store.c"
OPCODE_1A = ROOT / "von/i960/recovered_sharc_opcode_1a.c"

I = 0x3F800000
TRIALS = [
    ([I, 0, 0, 0, I, 0, 0, 0, I, 0x41200000, 0x41A00000, 0x41F00000],
     [I, 0x40000000, 0x40400000],
     [0x41300000, 0x41B00000, 0x42040000]),
    ([0x40000000, 0, 0, 0, 0x40000000, 0, 0, 0, 0x40000000,
      0x3F000000, 0xBF9A0000, 0x42C80000],
     [0x3F900000, 0x40180000, 0x409A0000],
     [0x40300000, 0x40630000, 0x42DB4000]),
    ([I, 0x40000000, 0x40400000, 0, I, 0, 0, 0, I, 0, 0, 0],
     [I, I, I],
     [0x3F800000, 0x40400000, 0x40800000]),
    ([I, 0, 0, 0, I, 0, 0, 0, I, 0x3DCCCCCD, 0x3E4CCCCD, 0x3E99999A],
     [0, 0, 0],
     [0x3DCCCCCD, 0x3E4CCCCD, 0x3E99999A]),
]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-07-") as directory:
        library = Path(directory) / "opcode-07.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", f"-I{ROOT}", str(SOURCE), str(OPCODE_1A),
             "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.recovered_sharc_opcode_07_store.argtypes = [
            ctypes.POINTER(ctypes.c_uint32)] * 2
        lib.recovered_sharc_opcode_07_store.restype = None
        affine = lib.recovered_sharc_opcode_1a_affine
        affine.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 3
        affine.restype = None

        words12 = ctypes.c_uint32 * 12
        words3 = ctypes.c_uint32 * 3
        pattern = words12(*[(i * 0x01010101) & 0xFFFFFFFF for i in range(12)])
        stored = words12()
        lib.recovered_sharc_opcode_07_store(pattern, stored)
        assert list(stored) == list(pattern), "identity copy"

        for state_in, vector_in, expected in TRIALS:
            lib.recovered_sharc_opcode_07_store(words12(*state_in), stored)
            vector = words3(*vector_in)
            output = words3()
            affine(vector, stored, output)
            assert list(output) == expected, (
                f"trial {state_in[9:]}: {list(output)!r}")
        print("PASS: verbatim store, 4 live trials end to end")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
