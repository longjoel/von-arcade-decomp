#!/usr/bin/env python3
"""Validate the reusable normal-path C contract for SHARC opcode 0x47."""

from __future__ import annotations

import ctypes
import math
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode47.so"
        subprocess.run(
            [
                "cc", "-shared", "-fPIC", "-O2",
                str(ROOT / "von/i960/recovered_sharc_opcode_47.c"),
                "-lm", "-o", str(library),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        lib = ctypes.CDLL(str(library))
        predicate = lib.recovered_sharc_opcode_47_predicate
        word_array = ctypes.c_uint32
        predicate.argtypes = [ctypes.POINTER(word_array),
                              ctypes.POINTER(word_array)]
        predicate.restype = ctypes.c_uint32

        def run(values, state):
            inputs = (word_array * 4)(*(ctypes.c_uint32.from_buffer_copy(
                ctypes.c_float(value)).value for value in values))
            states = (word_array * 7)(*(ctypes.c_uint32.from_buffer_copy(
                ctypes.c_float(value)).value for value in state))
            return predicate(inputs, states)

        state = (0.0, 0.0, 0.0, 3.0, -0.5, 0.0, 0.0)
        assert run((3.0, 4.0, 6.0, -2.0), state) == 0
        assert run((3.0, 4.0, 4.0, -2.0), state) == 1
        # The vertical interval is inclusive at both ends.
        assert run((0.0, 0.0, 6.0, 0.5), state) == 0
        assert run((0.0, 0.0, 6.0, -3.0), state) == 0
        assert run((0.0, 0.0, math.nan, 0.0), state) == 1
        assert run((math.nan, 0.0, 6.0, 0.0), state) == 1

    print("PASS: SHARC opcode-0x47 C predicate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
