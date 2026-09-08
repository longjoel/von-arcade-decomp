#!/usr/bin/env python3
"""Verify the SHARC opcode-0x05/0x06 stack discipline.

Pins the saturating depth counter (push caps at 7, pop floors at 0
with no rewind) and replays six live-hardware invariance points
through the trusted opcode-0x1a model: push, pop, overflow, and
drain runs never change the observable affine state
(von/build/probe_sharc_opcode_05_06.lua).
"""

from __future__ import annotations

import ctypes
import os
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "von/i960/recovered_sharc_stack_05_06.c"
OPCODE_1A = ROOT / "von/i960/recovered_sharc_opcode_1a.c"

I = 0x3F800000
S1 = [I, 0, 0, 0, I, 0, 0, 0, I, 0x41200000, 0x41A00000, 0x41F00000]
S2 = [0x40000000, 0, 0, 0, 0x40000000, 0, 0, 0, 0x40000000, 0, 0, 0]
V = [I, 0x40000000, 0x40400000]
R1 = [0x41300000, 0x41B00000, 0x42040000]
R2 = [0x40000000, 0x40800000, 0x40C00000]


class PopOut(ctypes.Structure):
    _fields_ = [("depth", ctypes.c_uint32), ("ptr", ctypes.c_uint32)]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="von-sharc-stk-") as directory:
        library = Path(directory) / "stack.so"
        subprocess.run(
            [os.environ.get("CC", "cc"), "-std=c99", "-O2", "-shared",
             "-fPIC", f"-I{ROOT}", str(SOURCE), str(OPCODE_1A),
             "-o", str(library)],
            check=True,
        )
        lib = ctypes.CDLL(str(library))
        lib.sharc_stack_push_depth.argtypes = [ctypes.c_uint32]
        lib.sharc_stack_push_depth.restype = ctypes.c_uint32
        lib.sharc_stack_pop.argtypes = [ctypes.c_uint32] * 2 + [
            ctypes.POINTER(PopOut)]
        lib.sharc_stack_pop.restype = None
        affine = lib.recovered_sharc_opcode_1a_affine
        affine.argtypes = [ctypes.POINTER(ctypes.c_uint32)] * 3
        affine.restype = None

        push = lib.sharc_stack_push_depth
        depth = 0
        for _ in range(9):
            depth = push(depth)
        assert depth == 7, depth
        out = PopOut()
        for _ in range(9):
            lib.sharc_stack_pop(depth, 0x30200, ctypes.byref(out))
            depth = out.depth
        assert depth == 0, depth
        lib.sharc_stack_pop(0, 0x30200, ctypes.byref(out))
        assert (out.depth, out.ptr) == (0, 0x30200), "empty no-op"
        lib.sharc_stack_pop(3, 0x30224, ctypes.byref(out))
        assert (out.depth, out.ptr) == (2, 0x30224 - 12), "rewind"

        words12 = ctypes.c_uint32 * 12
        words3 = ctypes.c_uint32 * 3
        vector = words3(*V)
        for state, expected in ((S1, R1), (S1, R1), (S2, R2),
                                (S2, R2), (S2, R2), (S2, R2)):
            output = words3()
            affine(vector, words12(*state), output)
            assert list(output) == expected, expected
        print("PASS: saturating discipline, 6 invariance goldens")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
