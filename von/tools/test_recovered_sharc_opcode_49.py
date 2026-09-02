#!/usr/bin/env python3
"""Validate the reusable normal-path C contract for SHARC opcode 0x49."""

from __future__ import annotations

import ctypes
import math
import struct
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def float_bits(value: float) -> int:
    return struct.unpack("=I", struct.pack("=f", value))[0]


def main() -> int:
    with tempfile.TemporaryDirectory() as directory:
        library = Path(directory) / "opcode49.so"
        subprocess.run(
            ["cc", "-shared", "-fPIC", "-O2",
             str(ROOT / "von/i960/recovered_sharc_opcode_49.c"),
             "-lm", "-o", str(library)],
            check=True, capture_output=True, text=True,
        )
        lib = ctypes.CDLL(str(library))
        predicate = lib.recovered_sharc_opcode_49_predicate
        word = ctypes.c_uint32
        predicate.argtypes = [ctypes.POINTER(word), ctypes.POINTER(word)]
        predicate.restype = ctypes.c_uint32

        def run(vector, state):
            inputs = (word * 4)(*(float_bits(value) for value in vector))
            states = (word * 5)(*(float_bits(value) for value in state))
            return predicate(inputs, states), tuple(int(value) for value in states)

        state = (0.0, 0.0, 0.0, 4.0, 5.0)
        result, unchanged = run((3.0, 4.0, 0.0, 0.0), state)
        assert result == 1 and unchanged == tuple(float_bits(v) for v in state)
        assert run((1.0, 2.0, 2.0, 0.0), state)[0] == 0
        assert run((0.0, 0.0, 0.0, 0.0),
                   (0.0, 0.0, 0.0, 0.0, 0.0))[0] == 1
        assert run((math.nan, 0.0, 0.0, 5.0), state)[0] == 1

    print("PASS: SHARC opcode-0x49 C predicate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
